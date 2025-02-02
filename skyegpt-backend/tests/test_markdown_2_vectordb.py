from Markdown2VectorDB import (split_markdown_to_header_texts,
                               import_file_to_document,
                               scan_and_import_markdowns_from_folder)
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

markdown_file_content = """
        # Header-11
        text under header-11
        ## Header-21
        text under header-21
        ## Header-22
        text under header-22
        ### Header-31
        text under header-31
        ### Header-32
        text under header-32
        # Header-12
        text under header-12
        ## Header-22
        text under header-23"""


def test_split_markdown_to_header_texts_all_headers():

    markdown_split_headers = ["#", "##", "###"]

    splits = split_markdown_to_header_texts(
        markdown_file_content,
        markdown_split_headers
    )

    expected_length = 7
    actual_length = len(splits)

    assert actual_length == expected_length, "Sample document has 7 headers and split outcome should be 7 documents"


def test_split_markdown_to_header_texts_top_two_headers():

    markdown_split_headers = ["#", "##"]

    splits = split_markdown_to_header_texts(
        markdown_file_content,
        markdown_split_headers
    )

    expected_length = 5
    actual_length = len(splits)
    assert actual_length == expected_length, "Sample document has 5 sections when split at # and ## headers"


def test_split_markdown_to_header_texts_top_level_headers():

    markdown_split_headers = ["#"]

    splits = split_markdown_to_header_texts(
        markdown_file_content,
        markdown_split_headers
    )

    expected_length = 2
    actual_length = len(splits)

    assert actual_length == expected_length, "Sample document has 2 sections when split at # headers"


def test_import_file_to_document_is_calling_functions_with_proper_arguments():
    collection_name = "test_collection_name"
    markdown_split_headers = ["#", "##"]
    file_name = "test_file_name"
    documentation_source = "test_skye"
    file_content = "# Test_file_content"

    with patch("Markdown2VectorDB.split_markdown_to_header_texts") as mock_split, \
            patch("ChromaSetup.create_document_from_split_texts") as mock_create_doc:

        mock_split.return_value = ["test_data", "data_doesnt_need_to_be_valid"]

        import_file_to_document(
            collection_name,
            markdown_split_headers,
            file_name,
            file_content,
            documentation_source
        )

        mock_split.assert_called_once_with(
            file_content,
            markdown_split_headers
        )

        mock_create_doc.assert_called_once_with(
            collection_name,
            mock_split.return_value,
            file_name,
            documentation_source
        )


def test_scan_and_import_markdowns_from_folder_2_files_success():
    collection_name = "test_collection"
    folder_path = "test_folder"
    markdown_split_headers = ["#", "##"]
    documentation_source = "test_skye"

    mock_files = [MagicMock(spec=Path), MagicMock(spec=Path)]
    mock_files[0].name = "test_file1.md"
    mock_files[1].name = "test_file2.md"

    mock_file = mock_open()
    mock_file.side_effect = [
        mock_open(read_data="# Content of test file 1").return_value,
        mock_open(read_data="# Content of test file 2").return_value
    ]

    with patch("Markdown2VectorDB.Path.rglob", return_value=mock_files), \
            patch("builtins.open", mock_file), \
            patch("Markdown2VectorDB.import_file_to_document") as mock_import:

        scan_and_import_markdowns_from_folder(
            collection_name,
            folder_path,
            markdown_split_headers,
            documentation_source
        )

        mock_import.assert_any_call(
            collection_name,
            markdown_split_headers,
            "test_file1",
            "# Content of test file 1",
            documentation_source
        )

        mock_import.assert_any_call(
            collection_name,
            markdown_split_headers,
            "test_file2",
            "# Content of test file 2",
            documentation_source
        )

    assert mock_import.call_count == 2, "Expected import_file_to_document to be called twice, once for each file."
