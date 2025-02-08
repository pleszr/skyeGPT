import requests
import os


def load_content_to_memory():
    url = 'https://innoveo.atlassian.net/wiki/rest/api/content'
    start = 0
    initial_params = {
        "type": "page",
        "spaceKey": "IPH",
        "limit": 100,
        "expand": "body.storage"
    }

    is_last_page = False
    while not is_last_page:
        response = requests.get(url, params=initial_params)
        data = response.json()
        pages = [result for result in data["results"]]
        if len(pages) == 0:
            is_last_page = True

        for page in pages:
            download_confluence_to_html(
                page["title"],
                page["body"]["storage"]["value"]
            )

        start += 100
        initial_params["start"] = start

    return ''


def download_confluence_to_html(
        title: str,
        content: str
):
    folder_path = "content/iph"
    os.makedirs(folder_path, exist_ok=True)

    trimmed_title = title.replace(" ", "-").replace("/", "-")
    file_path = os.path.join(folder_path, f"{trimmed_title}.html")

    with open(file_path, "w") as file:
        file.write(content)
