from unittest.mock import patch
from services.setup_services import IngestionService, DatabaseService
import pytest
from common import constants
from common.exceptions import VectorDBError, CollectionNotFoundError


@pytest.mark.asyncio
@patch("data_ingestion.scrapers.save_skye_documentation.download_skye_documentation_from_s3")
async def test_ingestion_service_download_skye_documentation_happy_path(mock_download_s3):
    service = IngestionService()
    test_version = "10.1"
    expected_result_dict = {"path": "/docs/10.1", "status": "downloaded"}

    mock_download_s3.return_value = expected_result_dict

    result = service.download_skye_documentation_to_server(test_version)

    mock_download_s3.assert_called_once_with(test_version)
    assert result == expected_result_dict


@pytest.mark.asyncio
@patch("data_ingestion.scrapers.save_skye_documentation.download_skye_documentation_from_s3")
async def test_ingestion_service_download_skye_documentation_file_not_found(mock_download_s3):
    service = IngestionService()
    test_version = "0.0"

    mock_download_s3.side_effect = FileNotFoundError("S3 file not found for this version")

    with pytest.raises(FileNotFoundError) as exc_info:
        service.download_skye_documentation_to_server(test_version)

    assert "S3 file not found for this version" in str(exc_info.value)
    mock_download_s3.assert_called_once_with(test_version)


@pytest.mark.asyncio
@patch("data_ingestion.scrapers.save_skye_documentation.download_skye_documentation_from_s3")
async def test_ingestion_service_download_skye_documentation_generic_error(mock_download_s3):
    service = IngestionService()
    test_version = "1.0"
    error_message = "Some other S3 issue"

    mock_download_s3.side_effect = Exception(error_message)

    with pytest.raises(Exception) as exc_info:
        service.download_skye_documentation_to_server(test_version)

    assert error_message in str(exc_info.value)
    mock_download_s3.assert_called_once_with(test_version)


@pytest.mark.asyncio
@patch("data_ingestion.scrapers.save_innoveo_partner_hub.download_innoveo_partner_hub")
async def test_ingestion_service_download_iph_happy_path(mock_download_iph):
    service = IngestionService()
    expected_result_dict = {"name": "iph_root", "type": "folder", "children": [{"name": "index.md", "type": "file"}]}

    mock_download_iph.return_value = expected_result_dict

    result = service.download_iph_to_server()

    mock_download_iph.assert_called_once_with()
    assert result == expected_result_dict


@pytest.mark.asyncio
@patch("data_ingestion.scrapers.save_innoveo_partner_hub.download_innoveo_partner_hub")
async def test_ingestion_service_download_iph_generic_error(mock_download_iph):
    service = IngestionService()
    error_message = "A sudden confluence connection error"

    mock_download_iph.side_effect = Exception(error_message)

    with pytest.raises(Exception) as exc_info:
        service.download_iph_to_server()

    assert error_message in str(exc_info.value)
    mock_download_iph.assert_called_once_with()


@pytest.mark.asyncio
@patch("common.utils.generate_local_folder_path_from_skye_version")
@patch("data_ingestion.persister.markdown_2_vector_db.scan_and_import_markdowns_from_folder")
async def test_ingestion_service_import_skyedoc_happy_path(mock_scan_and_import, mock_generate_path):
    service = IngestionService()
    test_skye_version = "12.1"
    test_markdown_headers = ["#", "##"]
    expected_folder_path = "/path/to/skyedoc/12.1"

    mock_generate_path.return_value = expected_folder_path

    service.import_skyedoc(test_skye_version, test_markdown_headers)

    mock_generate_path.assert_called_once_with(test_skye_version)
    mock_scan_and_import.assert_called_once_with(
        constants.SKYE_DOC_COLLECTION_NAME, expected_folder_path, test_markdown_headers
    )


@pytest.mark.asyncio
@patch("common.utils.generate_local_folder_path_from_skye_version")
@patch("data_ingestion.persister.markdown_2_vector_db.scan_and_import_markdowns_from_folder")
async def test_ingestion_service_import_skyedoc_generic_error(mock_scan_and_import, mock_generate_path):
    service = IngestionService()
    test_skye_version = "12.2"
    test_markdown_headers = ["#"]
    expected_folder_path = "/path/to/skyedoc/12.2"
    error_message = "Something went wrong during import"

    mock_generate_path.return_value = expected_folder_path
    mock_scan_and_import.side_effect = Exception(error_message)

    with pytest.raises(Exception) as exc_info:
        service.import_skyedoc(test_skye_version, test_markdown_headers)

    assert error_message in str(exc_info.value)
    mock_generate_path.assert_called_once_with(test_skye_version)
    mock_scan_and_import.assert_called_once_with(
        constants.SKYE_DOC_COLLECTION_NAME, expected_folder_path, test_markdown_headers
    )


@pytest.mark.asyncio
@patch("data_ingestion.persister.markdown_2_vector_db.scan_and_import_markdowns_from_folder")
async def test_ingestion_service_import_iph_happy_path(mock_scan_and_import):
    service = IngestionService()
    test_markdown_headers = ["#", "##"]

    service.import_iph(test_markdown_headers)

    mock_scan_and_import.assert_called_once_with(
        constants.IPH_DOC_COLLECTION_NAME, constants.IPH_LOCAL_FOLDER_LOCATION, test_markdown_headers
    )


@pytest.mark.asyncio
@patch("data_ingestion.persister.markdown_2_vector_db.scan_and_import_markdowns_from_folder")
async def test_ingestion_service_import_iph_generic_error(mock_scan_and_import):
    service = IngestionService()
    test_markdown_headers = ["#"]
    error_message = "Something went wrong during IPH import"

    mock_scan_and_import.side_effect = Exception(error_message)

    with pytest.raises(Exception) as exc_info:
        service.import_iph(test_markdown_headers)

    assert error_message in str(exc_info.value)
    mock_scan_and_import.assert_called_once_with(
        constants.IPH_DOC_COLLECTION_NAME, constants.IPH_LOCAL_FOLDER_LOCATION, test_markdown_headers
    )


@pytest.mark.asyncio
@patch("database.vectordb_client.delete_collection")
async def test_database_service_delete_collection_happy_path(mock_delete_collection_client):
    service = DatabaseService()
    test_collection_name = "my_test_collection"

    service.delete_collection(test_collection_name)

    mock_delete_collection_client.assert_called_once_with(test_collection_name)


@pytest.mark.asyncio
@patch("database.vectordb_client.delete_collection")
async def test_database_service_delete_collection_not_found_error(mock_delete_collection_client):
    service = DatabaseService()
    test_collection_name = "non_existent_collection"

    mock_delete_collection_client.side_effect = CollectionNotFoundError("Collection not found")

    with pytest.raises(CollectionNotFoundError) as exc_info:
        service.delete_collection(test_collection_name)

    assert "Collection not found" in str(exc_info.value)
    mock_delete_collection_client.assert_called_once_with(test_collection_name)


@pytest.mark.asyncio
@patch("database.vectordb_client.delete_collection")
async def test_database_service_delete_collection_vector_db_error(mock_delete_collection_client):
    service = DatabaseService()
    test_collection_name = "another_collection"

    mock_delete_collection_client.side_effect = VectorDBError("Generic DB error")

    with pytest.raises(VectorDBError) as exc_info:
        service.delete_collection(test_collection_name)

    assert "Generic DB error" in str(exc_info.value)
    mock_delete_collection_client.assert_called_once_with(test_collection_name)


@pytest.mark.asyncio
@patch("database.vectordb_client.number_of_documents_in_collection")
async def test_database_service_number_of_documents_happy_path(mock_number_of_documents_client):
    service = DatabaseService()
    test_collection_name = "my_doc_collection"
    expected_count = 123

    mock_number_of_documents_client.return_value = expected_count

    result = service.number_of_documents_in_collection(test_collection_name)

    mock_number_of_documents_client.assert_called_once_with(test_collection_name)
    assert result == expected_count


@pytest.mark.asyncio
@patch("database.vectordb_client.number_of_documents_in_collection")
async def test_database_service_number_of_documents_vector_db_error(mock_number_of_documents_client):
    service = DatabaseService()
    test_collection_name = "collection_with_db_error"

    mock_number_of_documents_client.side_effect = VectorDBError("VectorDB error during count")

    with pytest.raises(VectorDBError) as exc_info:
        service.number_of_documents_in_collection(test_collection_name)

    assert "VectorDB error during count" in str(exc_info.value)
    mock_number_of_documents_client.assert_called_once_with(test_collection_name)


@pytest.mark.asyncio
@patch("database.vectordb_client.number_of_documents_in_collection")
async def test_database_service_number_of_documents_generic_exception(mock_number_of_documents_client):
    service = DatabaseService()
    test_collection_name = "collection_with_generic_error"
    error_message = "An unexpected issue occurred"

    mock_number_of_documents_client.side_effect = Exception(error_message)

    with pytest.raises(Exception) as exc_info:
        service.number_of_documents_in_collection(test_collection_name)

    assert error_message in str(exc_info.value)
    mock_number_of_documents_client.assert_called_once_with(test_collection_name)
