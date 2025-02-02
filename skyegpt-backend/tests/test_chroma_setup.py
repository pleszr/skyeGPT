from ChromaSetup import (delete_collection,
                         create_collection,
                         set_chroma_client,
                         verify_if_collection_exists,
                         add_document_to_collection,
                         get_collection_by_name,
                         number_of_documents_in_collection,
                         create_document_from_split_texts,
                         create_collection_if_needed,
                         save_settings_to_settings_store,
                         chroma_settings_store,
                         setup_chroma)
import chromadb
from chromadb.errors import InvalidCollectionException
from unittest.mock import patch
import pytest
from unittest.mock import MagicMock


client = chromadb.Client()


@pytest.fixture(scope="module", autouse=True)
def setup_chroma_client():
    set_chroma_client(client)


def test_delete_collection():
    collection_name = "test_collection_name"
    create_collection(collection_name)

    delete_collection(collection_name)

    is_collection_deleted = not verify_if_collection_exists(collection_name)
    assert is_collection_deleted


def test_verify_if_collection_exists_when_exists():
    collection_name = "test_collection_name_unique"
    create_collection(collection_name)
    does_collection_exist = verify_if_collection_exists(collection_name)
    assert does_collection_exist


def test_verify_if_collection_exists_when_doesnt_exist():
    collection_name = "test_collection_name"
    does_collection_exist = verify_if_collection_exists(collection_name)
    assert not does_collection_exist


def test_create_collection():
    collection_name = "test_collection_name"
    create_collection(collection_name)

    does_collection_exist = verify_if_collection_exists(collection_name)
    assert does_collection_exist


@patch("ChromaSetup.get_collection_by_name")
@patch("uuid.uuid4")
def test_add_document_to_collection(mock_uuid4, mock_get_collection_by_name):
    collection_name = "test_collection"
    document = "# This is a test document."
    metadata = {"key1": "value1", "key2": "value2"}

    mock_collection = MagicMock()
    mock_get_collection_by_name.return_value = mock_collection

    mock_uuid4.return_value = "test_uuid4_value"

    result_uuid = add_document_to_collection(
        collection_name,
        document,
        metadata
    )

    mock_get_collection_by_name.assert_called_once_with(collection_name)
    mock_collection.add.assert_called_once_with(
        documents=document,
        ids="test_uuid4_value",
        metadatas=metadata
    )

    assert result_uuid == "test_uuid4_value"


@patch("ChromaSetup.chroma_client.get_collection")
def test_get_collection_by_name(mock_get_collection):
    collection_name = "test_collection_name"

    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection

    result_collection = get_collection_by_name(
        collection_name
    )

    mock_get_collection.assert_called_once_with(
        name=collection_name
    )
    assert result_collection == mock_collection


@patch("ChromaSetup.chroma_client.get_collection")
def test_number_of_documents_in_collection(mock_get_collection):
    collection_name = "test_collection_name"
    number_of_documents = 5

    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection
    mock_collection.count.return_value = number_of_documents

    actual_number_of_documents = number_of_documents_in_collection(collection_name)

    mock_collection.count.assert_called_once_with()
    mock_get_collection.assert_called_once_with(collection_name)
    assert actual_number_of_documents == number_of_documents


@patch("ChromaSetup.number_of_documents_in_collection")
@patch("ChromaSetup.documentation_link_generator")
@patch("ChromaSetup.add_document_to_collection")
def test_create_document_from_split_texts_from_file(mock_add_document_to_collection,
                                                    mock_documentation_link_generator,
                                                    mock_number_of_documents_in_collection):
    collection_name = "test_collection"
    content_text_array = ["text_1", "text_2", "text_3", "text_4"]
    file_name = "test_file_name"
    documentation_source = "test_documentation_source"

    documentation_link = "documentation_link"
    mock_documentation_link_generator.return_value = documentation_link

    metadata = {
        "file_name": file_name,
        "documentation_link": documentation_link
    }

    mock_number_of_documents_in_collection.return_value = len(content_text_array)

    create_document_from_split_texts(
        collection_name,
        content_text_array,
        file_name,
        documentation_source
    )

    assert mock_add_document_to_collection.call_count == len(content_text_array)

    mock_add_document_to_collection.assert_any_call(
        collection_name,
        content_text_array[0],
        metadata
    )
    mock_add_document_to_collection.assert_any_call(
        collection_name,
        content_text_array[1],
        metadata
    )
    mock_add_document_to_collection.assert_any_call(
        collection_name,
        content_text_array[2],
        metadata
    )
    mock_add_document_to_collection.assert_any_call(
        collection_name,
        content_text_array[3],
        metadata
    )


@patch("ChromaSetup.create_collection")
@patch("ChromaSetup.get_collection_by_name")
def test_create_collection_if_needed_yes_needed(mock_get_collection_by_name,
                                                mock_create_collection):
    collection_name = "test_collection"

    mock_collection = MagicMock()
    mock_get_collection_by_name.return_value = mock_collection

    create_collection_if_needed(collection_name)

    mock_create_collection.assert_not_called()


@patch("ChromaSetup.create_collection", autospec=True)
@patch("ChromaSetup.get_collection_by_name")
def test_create_collection_if_needed_not_needed(mock_get_collection_by_name,
                                                mock_create_collection):
    collection_name = "test_collection"

    mock_get_collection_by_name.side_effect = chromadb.errors.InvalidCollectionException

    create_collection_if_needed(collection_name)

    mock_create_collection.assert_called_once_with(collection_name)


def test__settings_to_settings_store():
    number_of_chroma_results = 2
    gpt_model = "gpt-4o-mini"
    gpt_temperature = 0.1
    gpt_developer_prompt = "dev prompt"

    number_of_settings = len(chroma_settings_store)
    assert number_of_settings == 0

    save_settings_to_settings_store(
        number_of_chroma_results,
        gpt_model,
        gpt_temperature,
        gpt_developer_prompt
    )

    number_of_settings = len(chroma_settings_store)
    assert number_of_settings == 4


@patch("ImportFromS3.download_files_from_s3_bucket")
@patch("ChromaSetup.number_of_documents_in_collection")
@patch("Markdown2VectorDB.scan_and_import_markdowns_from_folder")
@patch("ChromaSetup.create_collection_if_needed")
@patch("ChromaSetup.save_settings_to_settings_store")
def test_setup_chroma(mock_save_settings_to_settings_store,
                      mock_create_collection_if_needed,
                      mock_scan_and_import_markdowns_from_folder,
                      mock_number_of_documents_in_collection,
                      mock_download_files_from_s3_bucket
                      ):
    collection_name = "example_collection_name"
    should_import = True
    folder_path = "example/folder/path"
    documentation_source = "test_documentation_source"
    number_of_chroma_results = 5
    markdown_split_headers = ["text_content1", "text_content2", "text_content3"]
    gpt_model = "gpt-4o-mini"
    gpt_temperature = 0.1
    gpt_developer_prompt = "test_developer_prompt"
    expected_number_of_documents = len(markdown_split_headers)
    s3_bucket = "test_bucket"
    s3_folder_prefix = "test/"
    s3_local_folder = "test/content"
    documentation_selector = {
        "s3": True,
        "innoveo_partner_hub": False
    }

    mock_number_of_documents_in_collection.return_value = expected_number_of_documents

    actual_number_of_documents = setup_chroma(
        collection_name,
        should_import,
        folder_path,
        documentation_source,
        number_of_chroma_results,
        markdown_split_headers,
        gpt_model,
        gpt_temperature,
        gpt_developer_prompt,
        documentation_selector,
        s3_bucket,
        s3_folder_prefix,
        s3_local_folder
    )

    mock_save_settings_to_settings_store.assert_called_once_with(
        number_of_chroma_results,
        gpt_model,
        gpt_temperature,
        gpt_developer_prompt
    )
    mock_create_collection_if_needed.assert_called_once_with(collection_name)
    mock_scan_and_import_markdowns_from_folder.assert_called_once_with(
        collection_name,
        folder_path,
        markdown_split_headers,
        documentation_source
    )

    mock_download_files_from_s3_bucket.assert_called_once_with(
        s3_bucket,
        s3_folder_prefix,
        s3_local_folder
    )

    assert actual_number_of_documents == expected_number_of_documents
