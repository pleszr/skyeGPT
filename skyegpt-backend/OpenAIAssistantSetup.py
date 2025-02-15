from openai import OpenAI
from pathlib import Path
import ImportFromS3
import Confluence2Text

client = OpenAI()
assistant_settings_store = {}


def setup_openai_assistant(
        assistant_name: str,
        assistant_instructions: str,
        gpt_model: str,
        temperature: float,
        new_vector_store_name: str,
        existing_vector_store_id: str,
        folder_path: str,
        file_extension: str,
        documentation_selector: dict[str, bool],
        s3_bucket: str,
        s3_folder_prefix: str,
        s3_local_folder: str,
        confl_api_endpoint: str,
        confl_space_key: str,
        confl_save_path: str
):

    assistant_id = find_or_create_assistant(
        assistant_name,
        assistant_instructions,
        gpt_model,
        temperature
    )

    if documentation_selector.get("s3"):
        ImportFromS3.download_files_from_s3_bucket(
            s3_bucket,
            s3_folder_prefix,
            s3_local_folder
        )

    if documentation_selector.get("innoveo_partner_hub") is True:
        Confluence2Text.download_public_confluence_as_text(
            confl_api_endpoint,
            confl_space_key,
            confl_save_path
        )

    if existing_vector_store_id:
        vector_store_id = existing_vector_store_id
    else:
        vector_store_id = create_vector_store(new_vector_store_name)
        scan_folder_and_upload_to_vector_store(
            vector_store_id,
            folder_path,
            file_extension
        )
    add_vector_store_to_assistant(
        vector_store_id,
        assistant_id
    )
    number_of_documents = number_of_files_for_vector_store(vector_store_id)
    return (f"Assistant '{assistant_id}' created with vector store '{vector_store_id}' "
            f"and {number_of_documents} documents were uploaded.")


def find_or_create_assistant(
        assistant_name: str,
        assistant_instructions: str,
        gpt_model: str,
        temperature: float
):
    my_assistant = find_assistant_by_name(assistant_name)
    if my_assistant:
        print(f"Assistant with name: {assistant_name} found. Id is {my_assistant.id}")
    else:
        my_assistant = create_assistant(
            assistant_name,
            assistant_instructions,
            gpt_model,
            temperature
        )
        print(my_assistant)
        print(f"No assistant with name {assistant_name} found. Creating one...")
    assistant_settings_store["assistant_id"] = my_assistant.id
    return my_assistant.id


def find_assistant_by_name(
        assistant_name: str
):
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit=100,
    )
    matching_assistant = next(
        (assistant for assistant in my_assistants.data if assistant.name == assistant_name),
        None
    )
    return matching_assistant


def create_assistant(
        assistant_name: str,
        assistant_instructions: str,
        gpt_model: str,
        temperature: float
):
    my_assistant = client.beta.assistants.create(
        instructions=assistant_instructions,
        name=assistant_name,
        tools=[{"type": "file_search"}],
        model=gpt_model,
        temperature=temperature
    )
    return my_assistant


def create_vector_store(
    vector_store_name: str
):
    vector_store = client.beta.vector_stores.create(
        name=vector_store_name
    )
    print(f"Vector store with name {vector_store.name} and id {vector_store.id} successfully created")
    return vector_store.id


def scan_folder_and_upload_to_vector_store(
        vector_store_id: str,
        folder: str,
        file_extension: str
):
    folder = Path(folder)
    for file in folder.rglob(f"*.{file_extension}"):
        upload_file_and_add_to_vector_store(
            vector_store_id,
            str(file)
        )


def upload_file_and_add_to_vector_store(
        vector_store_id: str,
        file_path: str

):
    uploaded_file_id = upload_file(file_path)
    add_file_to_vector_store(
        vector_store_id,
        uploaded_file_id
    )
    print(f"Number of files uploaded so far: {number_of_files_for_vector_store(vector_store_id)}")


def upload_file(
        file_path: str
):
    uploaded_file = client.files.create(
        file=open(file_path, "rb"),
        purpose="assistants"
    )
    print(f"File successfully uploaded. ID: {uploaded_file.id}")
    return uploaded_file.id


def add_file_to_vector_store(
        vector_store_id: str,
        file_id: str
):
    client.beta.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file_id
    )
    print(f"File {file_id} successfully added to vector_store {vector_store_id}")


def number_of_files_for_vector_store(
        vector_store_id
):
    number_of_files = 0
    files = client.beta.vector_stores.files.list(
        vector_store_id=vector_store_id,
        limit=100
    )
    while files.has_more:
        number_of_files += 100
        last_id = files.last_id
        files = client.beta.vector_stores.files.list(
            vector_store_id=vector_store_id,
            limit=100,
            after=last_id
        )
    number_of_files += len(files.data)
    return number_of_files


def add_vector_store_to_assistant(
        vector_store_id: str,
        assistant_id: str
):
    client.beta.assistants.update(
        assistant_id,
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store_id]
            }
        }
    )
