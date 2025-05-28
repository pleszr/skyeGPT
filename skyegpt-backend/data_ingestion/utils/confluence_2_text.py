import requests
import os
import multiprocessing as mp
from common.utils import convert_html_to_md
import time
from .process_wrapper import create_process, start_process, join_process
from fastapi import HTTPException


def download_public_confluence_as_text(url: str, space_key: str, save_path: str):
    print(f"Saving confluence pages with space-key: {space_key} started")
    queue = mp.Queue()
    saved_count = mp.Value("i", 0)
    os.makedirs(save_path, exist_ok=True)
    start_time = time.time()

    producer_process = create_process(target=producer_fetch_pages_from_confluence, args=(url, space_key, queue))
    start_process(producer_process)

    consumer_processes = []
    number_of_threads = int(os.getenv("NUMBER_OF_MAX_THREADS"))
    for _ in range(number_of_threads):
        consumer_process = create_process(target=consumer_save_page_as_markdown, args=(save_path, queue, saved_count))
        start_process(consumer_process)
        consumer_processes.append(consumer_process)

    join_process(producer_process)
    for x in range(number_of_threads):
        queue.put(None)

    for consumer_process in consumer_processes:
        join_process(consumer_process)

    print(
        f"Saving confluence pages with space-key: {space_key} finished."
        f"Elapsed seconds: {time.time()-start_time:.0f}. "
        f"Saved files: {saved_count.value}"
    )


def producer_fetch_pages_from_confluence(url: str, space_key: str, queue: mp.Queue):
    start_at = 0
    request_params = {"type": "page", "spaceKey": space_key, "limit": 100, "expand": "body.storage"}

    is_last_page = False
    while not is_last_page:
        try:
            response = requests.get(url, params=request_params)
            response_data = response.json()
        except Exception as e:
            error_message = f"Could not gather data from {url} with parameters: {request_params}"
            print(error_message, e)
            raise HTTPException(status_code=500, detail=error_message)

        for result in response_data["results"]:
            queue.put(result)

        paginated_nr_of_results = len(response_data["results"])
        if paginated_nr_of_results == 0:
            is_last_page = True
        print(f"Added {paginated_nr_of_results} pages to the Queue.")

        start_at += 100
        request_params["start"] = start_at


def consumer_save_page_as_markdown(folder_path: str, queue: mp.Queue, saved_count: mp.Value):
    print(f"Consumer process started")
    while True:
        page = queue.get()
        if page is None:
            break

        file_name = page["id"]
        file_content_html = f"<p>{page['title']}</p>" + page["body"]["storage"]["value"]
        file_content_md = convert_html_to_md(file_content_html)

        file_path = os.path.join(folder_path, f"{file_name}.md")

        with open(file_path, "w") as file:
            file.write(file_content_md)

        with saved_count.get_lock():
            saved_count.value += 1
