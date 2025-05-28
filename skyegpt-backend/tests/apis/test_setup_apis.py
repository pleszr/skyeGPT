from unittest.mock import MagicMock
import pytest
from apis.schemas.requests import SkyeVersionRequest, ImportRequest
from apis.schemas.responses import DownloadResponse, ImportResponse
from apis.setup_apis import download_skye_documentation, download_iph, delete_collection, import_to_database
from fastapi import HTTPException
from common import message_bundle, constants
from common.exceptions import CollectionNotFoundError


@pytest.mark.asyncio
async def test_download_skye_documentation_happy_path():
    test_skye_version = "10.0"
    test_request = SkyeVersionRequest(skye_major_version=test_skye_version)
    expected_tree_structure = {"name": "skye-10.0", "type": "folder", "children": []}

    mock_ingestion_service = MagicMock()
    mock_ingestion_service.download_skye_documentation_to_server = MagicMock(return_value=expected_tree_structure)

    response = await download_skye_documentation(request=test_request, ingestion_service=mock_ingestion_service)

    mock_ingestion_service.download_skye_documentation_to_server.assert_called_once_with(test_skye_version)
    assert isinstance(response, DownloadResponse), "Response should be an instance of DownloadResponse"
    assert response.folder_content == expected_tree_structure


@pytest.mark.asyncio
async def test_download_skye_documentation_file_not_found():
    not_existing_skye_version = "0.0"
    test_request = SkyeVersionRequest(skye_major_version=not_existing_skye_version)

    mock_ingestion_service = MagicMock()
    mock_ingestion_service.download_skye_documentation_to_server = MagicMock(
        side_effect=FileNotFoundError("Mocked FileNotFoundError")
    )

    with pytest.raises(HTTPException) as exc_info:
        await download_skye_documentation(request=test_request, ingestion_service=mock_ingestion_service)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == message_bundle.VERSION_DOES_NOT_EXISTS
    mock_ingestion_service.download_skye_documentation_to_server.assert_called_once_with(not_existing_skye_version)


@pytest.mark.asyncio
async def test_download_iph_happy_path():
    expected_tree_structure = {"name": "iph_root", "type": "folder", "children": [{"name": "page.md", "type": "file"}]}

    mock_ingestion_service = MagicMock()
    mock_ingestion_service.download_iph_to_server = MagicMock(return_value=expected_tree_structure)

    response = await download_iph(ingestion_service=mock_ingestion_service)

    mock_ingestion_service.download_iph_to_server.assert_called_once_with()
    assert isinstance(response, DownloadResponse), "Response should be an instance of DownloadResponse"
    assert response.folder_content == expected_tree_structure


@pytest.mark.asyncio
async def test_delete_collection_happy_path():
    test_collection_name = "test_collection_to_delete"

    mock_db_service = MagicMock()
    mock_db_service.delete_collection = MagicMock()

    response = await delete_collection(collection_name=test_collection_name, db_service=mock_db_service)

    mock_db_service.delete_collection.assert_called_once_with(test_collection_name)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_collection_not_found():
    test_collection_name = "non_existent_collection"

    mock_db_service = MagicMock()
    mock_db_service.delete_collection = MagicMock(side_effect=CollectionNotFoundError("Mocked CollectionNotFoundError"))

    with pytest.raises(HTTPException) as exc_info:
        await delete_collection(collection_name=test_collection_name, db_service=mock_db_service)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == message_bundle.COLLECTION_NOT_FOUND
    mock_db_service.delete_collection.assert_called_once_with(test_collection_name)


@pytest.mark.asyncio
async def test_import_to_database_skyedoc_only_happy_path():
    test_markdown_split_headers = ["#", "##"]
    test_skye_version = "10.0"
    expected_doc_count = 100

    mock_skyedoc_config = MagicMock()
    mock_skyedoc_config.enabled = True
    mock_skyedoc_config.skye_major_version = test_skye_version

    mock_iph_config = MagicMock()
    mock_iph_config.enabled = False

    mock_imports_config = MagicMock()
    mock_imports_config.skyedoc = mock_skyedoc_config
    mock_imports_config.innoveo_partner_hub = mock_iph_config

    test_request = MagicMock(spec=ImportRequest)
    test_request.markdown_split_headers = test_markdown_split_headers
    test_request.imports = mock_imports_config

    mock_ingestion_service = MagicMock()
    mock_ingestion_service.import_skyedoc = MagicMock()
    mock_ingestion_service.import_iph = MagicMock()

    mock_database_service = MagicMock()
    mock_database_service.number_of_documents_in_collection = MagicMock(return_value=expected_doc_count)

    response = await import_to_database(
        request=test_request, ingestion_service=mock_ingestion_service, database_service=mock_database_service
    )

    mock_ingestion_service.import_skyedoc.assert_called_once_with(test_skye_version, test_markdown_split_headers)
    mock_ingestion_service.import_iph.assert_not_called()
    mock_database_service.number_of_documents_in_collection.assert_called_once_with(constants.SKYE_DOC_COLLECTION_NAME)
    assert isinstance(response, ImportResponse)
    assert response.number_of_documents == expected_doc_count


@pytest.mark.asyncio
async def test_import_to_database_iph_only_happy_path():
    test_markdown_split_headers = ["#"]
    expected_doc_count = 50

    mock_skyedoc_config = MagicMock()
    mock_skyedoc_config.enabled = False
    mock_skyedoc_config.skye_major_version = None

    mock_iph_config = MagicMock()
    mock_iph_config.enabled = True

    mock_imports_config = MagicMock()
    mock_imports_config.skyedoc = mock_skyedoc_config
    mock_imports_config.innoveo_partner_hub = mock_iph_config

    test_request = MagicMock(spec=ImportRequest)
    test_request.markdown_split_headers = test_markdown_split_headers
    test_request.imports = mock_imports_config

    mock_ingestion_service = MagicMock()
    mock_ingestion_service.import_skyedoc = MagicMock()
    mock_ingestion_service.import_iph = MagicMock()

    mock_database_service = MagicMock()
    mock_database_service.number_of_documents_in_collection = MagicMock(return_value=expected_doc_count)

    response = await import_to_database(
        request=test_request, ingestion_service=mock_ingestion_service, database_service=mock_database_service
    )

    mock_ingestion_service.import_skyedoc.assert_not_called()
    mock_ingestion_service.import_iph.assert_called_once_with(test_markdown_split_headers)
    mock_database_service.number_of_documents_in_collection.assert_called_once_with(constants.SKYE_DOC_COLLECTION_NAME)
    assert isinstance(response, ImportResponse)
    assert response.number_of_documents == expected_doc_count


@pytest.mark.asyncio
async def test_import_to_database_both_enabled_happy_path():
    test_markdown_split_headers = ["#", "##", "###"]
    test_skye_version = "9.16"
    expected_doc_count = 200

    mock_skyedoc_config = MagicMock()
    mock_skyedoc_config.enabled = True
    mock_skyedoc_config.skye_major_version = test_skye_version

    mock_iph_config = MagicMock()
    mock_iph_config.enabled = True

    mock_imports_config = MagicMock()
    mock_imports_config.skyedoc = mock_skyedoc_config
    mock_imports_config.innoveo_partner_hub = mock_iph_config

    test_request = MagicMock(spec=ImportRequest)
    test_request.markdown_split_headers = test_markdown_split_headers
    test_request.imports = mock_imports_config

    mock_ingestion_service = MagicMock()
    mock_ingestion_service.import_skyedoc = MagicMock()
    mock_ingestion_service.import_iph = MagicMock()

    mock_database_service = MagicMock()
    mock_database_service.number_of_documents_in_collection = MagicMock(return_value=expected_doc_count)

    response = await import_to_database(
        request=test_request, ingestion_service=mock_ingestion_service, database_service=mock_database_service
    )

    mock_ingestion_service.import_skyedoc.assert_called_once_with(test_skye_version, test_markdown_split_headers)
    mock_ingestion_service.import_iph.assert_called_once_with(test_markdown_split_headers)
    mock_database_service.number_of_documents_in_collection.assert_called_once_with(constants.SKYE_DOC_COLLECTION_NAME)
    assert isinstance(response, ImportResponse)
    assert response.number_of_documents == expected_doc_count


@pytest.mark.asyncio
async def test_import_to_database_no_import_selected_error():
    test_markdown_split_headers = ["#"]

    mock_skyedoc_config = MagicMock()
    mock_skyedoc_config.enabled = False
    mock_skyedoc_config.skye_major_version = None

    mock_iph_config = MagicMock()
    mock_iph_config.enabled = False

    mock_imports_config = MagicMock()
    mock_imports_config.skyedoc = mock_skyedoc_config
    mock_imports_config.innoveo_partner_hub = mock_iph_config

    test_request = MagicMock(spec=ImportRequest)
    test_request.markdown_split_headers = test_markdown_split_headers
    test_request.imports = mock_imports_config

    mock_ingestion_service = MagicMock()
    mock_ingestion_service.import_skyedoc = MagicMock()
    mock_ingestion_service.import_iph = MagicMock()

    mock_database_service = MagicMock()
    mock_database_service.number_of_documents_in_collection = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await import_to_database(
            request=test_request, ingestion_service=mock_ingestion_service, database_service=mock_database_service
        )

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == message_bundle.NO_IMPORT_SELECTED
    mock_ingestion_service.import_skyedoc.assert_not_called()
    mock_ingestion_service.import_iph.assert_not_called()
    mock_database_service.number_of_documents_in_collection.assert_not_called()
