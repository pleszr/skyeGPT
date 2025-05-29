"""Client for querying the SkyEGPT API endpoint."""

import requests
import uuid


def query_skyegpt(url: str, question: str, conversation_id: uuid) -> dict:
    """Send a question to the SkyEGPT API and return the JSON response."""
    headers = {"Content-Type": "application/json"}

    request_body = {"question": question, "conversation_id": conversation_id}

    response = requests.post(url, json=request_body, headers=headers)

    if response.status_code == 200:
        print(f"Successfully called the api with endpoint: {url} and request body: {request_body}")
        return response.json()
    else:
        raise Exception(f"Error while calling {url} with request body {request_body}. Response:", response)
