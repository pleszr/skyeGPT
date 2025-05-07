from ChromaClient import (delete_collection,
                          create_collection,
                          set_chroma_client,
                          verify_if_collection_exists,
                          add_to_collection,
                          get_collection_by_name,
                          number_of_documents_in_collection,
                          create_collection_if_needed)
from RagSetup import (save_settings_to_settings_store,
                      rag_settings_store,
                      setup_rag_pipeline)
import chromadb
from unittest.mock import patch, ANY
import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="function", autouse=True)
def setup_chroma_client():
    client = chromadb.Client()
    set_chroma_client(client)


def test_delete_collection():
    collection_name = "test_collection_name"
    create_collection(collection_name)
    delete_collection(collection_name)
    collection_exists = verify_if_collection_exists(collection_name)
    print(f"collection exists: {collection_exists}")
    assert not collection_exists


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


def test_add_document_to_collection():

    document = "# This is a test document."
    metadata = {"key1": "value1", "key2": "value2"}
    ids = ["test_id1"]

    mock_collection = MagicMock()

    add_to_collection(mock_collection,
                      document,
                      metadata,
                      ids)

    mock_collection.add.assert_called_once_with(documents=document,
                                                metadatas=metadata,
                                                ids=ids)


@patch("ChromaClient.chroma_client.get_collection")
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


@patch("ChromaClient.chroma_client.get_collection")
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


@patch("ChromaClient.chroma_client.get_or_create_collection")
def test_create_collection_if_needed_yes_needed(mock_get_or_create_collection):
    collection_name = "test_collection"

    mock_collection = MagicMock()
    mock_get_or_create_collection.return_value = mock_collection

    create_collection_if_needed(collection_name)

    mock_get_or_create_collection.assert_called_once_with(collection_name,
                                                          metadata=ANY)


def test_settings_to_settings_store():
    k_nearest_neighbors = 2
    gpt_model = "gpt-4o-mini"
    gpt_temperature = 0.1
    gpt_developer_prompt = "dev prompt"

    number_of_settings = len(rag_settings_store)
    assert number_of_settings == 0

    save_settings_to_settings_store(k_nearest_neighbors,
                                    gpt_model,
                                    gpt_temperature,
                                    gpt_developer_prompt)

    number_of_settings = len(rag_settings_store)
    assert number_of_settings == 4


@patch("Confluence2Text.download_public_confluence_as_text")
@patch("ImportFromS3.download_files_from_s3_bucket")
@patch("ChromaClient.number_of_documents_in_collection")
@patch("Markdown2VectorDB.scan_and_import_markdowns_from_folder")
@patch("ChromaClient.create_collection_if_needed")
@patch("RagSetup.save_settings_to_settings_store")
def test_setup_chroma(mock_save_settings_to_settings_store,
                      mock_create_collection_if_needed,
                      mock_scan_and_import_markdowns_from_folder,
                      mock_number_of_documents_in_collection,
                      mock_download_files_from_s3_bucket,
                      mock_confluence_as_text
                      ):
    collection_name = "example_collection_name"
    should_import = True
    folder_path = "example/folder/path"
    documentation_source = "test_documentation_source"
    k_nearest_neighbors = 5
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
    api_endpoint = "test_endpoint"
    space_key = "test_space_key"
    save_path = "test_save_path"

    mock_number_of_documents_in_collection.return_value = expected_number_of_documents

    setup_rag_pipeline(collection_name,
                       should_import,
                       folder_path,
                       k_nearest_neighbors,
                       markdown_split_headers,
                       gpt_model,
                       gpt_temperature,
                       gpt_developer_prompt,
                       documentation_selector,
                       s3_bucket,
                       s3_folder_prefix,
                       s3_local_folder,
                       api_endpoint,
                       space_key,
                       save_path)

    mock_save_settings_to_settings_store.assert_called_once_with(k_nearest_neighbors,
                                                                 gpt_model,
                                                                 gpt_temperature,
                                                                 gpt_developer_prompt)
    mock_create_collection_if_needed.assert_called_once_with(collection_name)

    mock_scan_and_import_markdowns_from_folder.assert_called_once_with(collection_name,
                                                                       folder_path,
                                                                       markdown_split_headers)
    mock_download_files_from_s3_bucket.assert_called_once_with(s3_bucket,
                                                               s3_folder_prefix,
                                                               s3_local_folder)

    mock_confluence_as_text.assert_not_called()
