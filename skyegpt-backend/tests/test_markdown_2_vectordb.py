# from pathlib import Path
# from data_ingestion.persister.markdown_2_vector_db import (_split_markdown_by_headers,
#                                scan_and_import_markdowns_from_folder,
#                                _chroma_import_producer,
#                                _chroma_import_consumer,
#                                _add_text_to_queue)
# from unittest.mock import patch, MagicMock, mock_open, call, ANY
# import multiprocessing as mp
# from queue import Empty
#
# markdown_file_content = """
#         # Header-11
#         text under header-11
#         ## Header-21
#         text under header-21
#         ## Header-22
#         text under header-22
#         ### Header-31
#         text under header-31
#         ### Header-32
#         text under header-32
#         # Header-12
#         text under header-12
#         ## Header-22
#         text under header-23"""
#
#
# def test_split_markdown_to_header_texts_all_headers():
#
#     markdown_split_headers = ["#", "##", "###"]
#
#     splits = _split_markdown_by_headers(
#         markdown_file_content,
#         markdown_split_headers
#     )
#
#     expected_length = 7
#     actual_length = len(splits)
#
#     assert actual_length == expected_length, "Sample document has 7 headers and split outcome should be 7 documents"
#
#
# def test_split_markdown_to_header_texts_top_two_headers():
#
#     markdown_split_headers = ["#", "##"]
#
#     splits = _split_markdown_by_headers(
#         markdown_file_content,
#         markdown_split_headers
#     )
#
#     expected_length = 5
#     actual_length = len(splits)
#     assert actual_length == expected_length, "Sample document has 5 sections when split at # and ## headers"
#
#
# def test_split_markdown_to_header_texts_top_level_headers():
#
#     markdown_split_headers = ["#"]
#
#     splits = _split_markdown_by_headers(
#         markdown_file_content,
#         markdown_split_headers
#     )
#
#     expected_length = 2
#     actual_length = len(splits)
#
#     assert actual_length == expected_length, "Sample document has 2 sections when split at # headers"
#
#
# @patch("ChromaClient.number_of_documents_in_collection")
# @patch("Markdown2VectorDB.join_process")
# @patch("Markdown2VectorDB.start_process")
# @patch("Markdown2VectorDB.create_process")
# def test_scan_and_import_markdowns_from_folder(
#         mock_create_process,
#         mock_start_process,
#         mock_join_process,
#         mock_number_of_documents,
#         monkeypatch
# ):
#     collection_name = "test_collection"
#     folder_path = "test/folder/path"
#     markdown_split_headers = ["#", "##"]
#
#     batch_size = 20
#     monkeypatch.setenv("RAG_BATCH_SIZE", str(batch_size))
#
#     mock_producer = MagicMock()
#     mock_consumer = MagicMock()
#     mock_create_process.side_effect = [mock_producer, mock_consumer]
#
#     scan_and_import_markdowns_from_folder(
#         collection_name,
#         folder_path,
#         markdown_split_headers
#     )
#
#     number_of_spawned_processes = 2
#     assert mock_create_process.call_count == number_of_spawned_processes
#     mock_create_process.assert_has_calls([
#         call(target=_chroma_import_producer, args=(
#             folder_path,
#             markdown_split_headers,
#             batch_size,
#             ANY
#         )),
#         call(target=_chroma_import_consumer, args=(
#             collection_name,
#             ANY
#         ))
#     ])
#     assert mock_start_process.call_count == 2
#     mock_start_process.assert_has_calls([
#         call(mock_producer),
#         call(mock_consumer)
#     ])
#
#     assert mock_join_process.call_count == 2
#     mock_join_process.assert_has_calls([
#         call(mock_producer),
#         call(mock_consumer)
#     ])
#
#     mock_number_of_documents.assert_called_once_with(collection_name)
#
#
# @patch("DocumentationLinkGenerator.select_doc_source_by_folder_path")
# @patch("Markdown2VectorDB.add_text_to_queue")
# @patch("Markdown2VectorDB.split_markdown_by_headers")
# @patch("builtins.open")
# @patch("pathlib.Path.rglob")
# def test_rag_import_producer(
#         mock_rglob,
#         mock_open_file,
#         mock_split_markdown,
#         mock_add_text_to_queue,
#         mock_select_doc_source
# ):
#     mock_files = [MagicMock(spec=Path), MagicMock(spec=Path)]
#     mock_files[0].name = "test_file1.md"
#     mock_files[1].name = "test_file2.md"
#
#     mock_rglob.return_value = mock_files
#
#     content_of_test_file_1 = "# Content of test file 1"
#     content_of_test_file_2 = "# Content of test file 2"
#     mock_file1 = mock_open(read_data=content_of_test_file_1).return_value
#     mock_file2 = mock_open(read_data=content_of_test_file_2).return_value
#     mock_open_file.side_effect = [mock_file1, mock_file2]
#
#     documentation_source = "test_documentation_source"
#     mock_select_doc_source.return_value = documentation_source
#
#     folder_path = "test/folder"
#     markdown_split_headers = ["#", "##"]
#     batch_size = 10
#     queue = "mock_queue"
#     content_of_files = "mock_text"
#     mock_split_markdown.return_value = content_of_files
#
#     _chroma_import_producer(folder_path,
#                            markdown_split_headers,
#                            batch_size,
#                            queue)
#
#     expected_split_markdown_by_headers_calls = [
#         call(content_of_test_file_1, markdown_split_headers),
#         call(content_of_test_file_2, markdown_split_headers)
#     ]
#     mock_split_markdown.assert_has_calls(expected_split_markdown_by_headers_calls,
#                                          any_order=True)
#     assert mock_split_markdown.call_count == 2
#
#     expected_add_text_calls = [
#         call(content_of_files, "test_file1", documentation_source, batch_size, queue),
#         call(content_of_files, "test_file2", documentation_source, batch_size, queue)
#     ]
#     mock_add_text_to_queue.assert_has_calls(expected_add_text_calls,
#                                             any_order=True)
#     assert mock_add_text_to_queue.call_count == 2
#
#
# @patch("DocumentationLinkGenerator.link_generator", return_value="test_docu_link")
# def test_add_text_to_queue(
#         mock_doc_link_generator
# ):
#     content_text_array = ["test text 1", "test text 2", "test text 3", "test text 4"]
#     file_name = "test_file_name"
#     documentation_source = "test_documentation_source"
#     batch_size = 2
#     queue = mp.Queue()
#
#     _add_text_to_queue(content_text_array, file_name, documentation_source, batch_size, queue)
#
#     assert mock_doc_link_generator.call_count == len(content_text_array)
#     mock_doc_link_generator.assert_any_call(file_name, documentation_source)
#
#     items = []
#     expected_batches = int(len(content_text_array)/batch_size)
#
#     for queue_item in range(expected_batches):
#         try:
#             item = queue.get(timeout=1)
#             items.append(item)
#         except Empty:
#             break
#     assert len(items) == expected_batches
#
#     documents1 = items[0]["documents"]
#     metadatas1 = items[0]["metadatas"]
#     ids1 = items[0]["ids"]
#     assert documents1 == ["test text 1", "test text 2"]
#     assert len(metadatas1) == 2
#     for metadata in metadatas1:
#         assert metadata["file_name"] == file_name
#         assert metadata["documentation_link"] == "test_docu_link"
#     assert len(ids1) == 2
#
#     documents2 = items[1]["documents"]
#     metadatas2 = items[1]["metadatas"]
#     ids2 = items[1]["ids"]
#     assert documents2 == ["test text 3", "test text 4"]
#     assert len(metadatas2) == 2
#     for metadata in metadatas2:
#         assert metadata["file_name"] == file_name
#         assert metadata["documentation_link"] == "test_docu_link", "Incorrect documentation_link in metadata"
#     assert len(ids2) == 2
#
#
# @patch("ChromaClient.add_to_collection")
# @patch("ChromaClient.get_collection_by_name")
# def test_chroma_import_consumer(mock_get_collection_by_name,
#                                 mock_add_to_collection):
#     batch1_ids = ["test_id1", "test_id2"]
#     batch1_documents = ["test text 1", "test text 2"]
#     batch1_metadatas = [
#         {
#             "file_name": "test_file_name1",
#             "documentation_link": "test_docu_link1"
#         },
#         {
#             "file_name": "test_file_name2",
#             "documentation_link": "test_docu_link2"
#         }
#     ]
#
#     batch2_ids = ["test_id3", "test_id4"]
#     batch2_documents = ["test text 3", "test text 4"]
#     batch2_metadatas = [
#         {
#             "file_name": "test_file_name3",
#             "documentation_link": "test_docu_link3"
#         },
#         {
#             "file_name": "test_file_name4",
#             "documentation_link": "test_docu_link4"
#         }
#     ]
#
#     collection_name = "test_collection_name"
#     queue = mp.Queue()
#
#     mock_collection = MagicMock()
#     mock_get_collection_by_name.return_value = mock_collection
#
#     queue.put({
#         "documents": batch1_documents,
#         "metadatas": batch1_metadatas,
#         "ids": batch1_ids,
#     })
#     queue.put({
#         "documents": batch2_documents,
#         "metadatas": batch2_metadatas,
#         "ids": batch2_ids,
#     })
#     queue.put(None)
#
#     _chroma_import_consumer(
#         collection_name,
#         queue
#     )
#
#     expected_add_to_collection_calls = [
#         call(mock_collection, documents=batch1_documents, metadatas=batch1_metadatas, ids=batch1_ids),
#         call(mock_collection, documents=batch2_documents, metadatas=batch2_metadatas, ids=batch2_ids)
#     ]
#     mock_add_to_collection.assert_has_calls(expected_add_to_collection_calls,
#                                             any_order=True)
