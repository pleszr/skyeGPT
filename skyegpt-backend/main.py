from fastapi import FastAPI, Query, Body
from fastapi.responses import StreamingResponse
import RagSetup
import ChromaClient
import RagPipeline
import OpenAIAssistantAsker
import OpenAIAssistantSetup
from openai import OpenAI
import uuid
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from Utils import format_to_sse, save_settings_stores, load_settings_stores
import signal


app = FastAPI()
chroma_client = chromadb.Client()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/setupChroma")
async def setup_chroma(request: dict = Body(...)):
    collection_name = request["chroma_parameters"]["collection_name"]
    should_import = request["chroma_parameters"]["should_import"]
    folder_path = request["chroma_parameters"]["folder_path"]
    documentation_source = request["chroma_parameters"]["documentation_source"]
    k_nearest_neighbors = request["chroma_parameters"]["k_nearest_neighbors"]
    markdown_split_headers = request["chroma_parameters"]["markdown_split_headers"]

    gpt_model = request["gpt_parameters"]["gpt_model"]
    gpt_temperature = request["gpt_parameters"]["gpt_temperature"]
    gpt_developer_prompt = request["gpt_parameters"]["gpt_developer_prompt"]

    documentation_selector = request["documentation_selector"]

    s3_bucket = request["documentation_sources"]["s3"]["s3_bucket"]
    s3_folder_prefix = request["documentation_sources"]["s3"]["s3_folder_prefix"]
    s3_local_folder = request["documentation_sources"]["s3"]["s3_local_folder"]

    number_of_uploaded_documents = RagSetup.setup_rag_pipeline(
                collection_name,
                should_import,
                folder_path,
                documentation_source,
                k_nearest_neighbors,
                markdown_split_headers,
                gpt_model,
                gpt_temperature,
                gpt_developer_prompt,
                documentation_selector,
                s3_bucket,
                s3_folder_prefix,
                s3_local_folder
            )
    return {"outcome": f"Chroma setup successful. Number of uploaded documents: {number_of_uploaded_documents}"}


@app.delete("/deleteCollection")
async def delete_collection(collection_name: str = Query(..., description="The name of the collection to delete")):
    ChromaClient.delete_collection(collection_name)


@app.post("/askChroma")
async def ask_chroma(request: dict = Body(...)):
    conversation_id = request["chroma_conversation_id"]
    question = request["question"]

    return StreamingResponse(
        format_to_sse(
            RagPipeline.ask_gpt_using_rag_pipeline(question, conversation_id)
        ),
        media_type="text/event-stream"
    )


@app.post("/askAssistant")
async def ask_assistant(request: dict = Body(...)):
    question = request["question"]
    thread_id = request["thread_id"]

    return StreamingResponse(
        format_to_sse(
            OpenAIAssistantAsker.ask_question(
                thread_id, question
            )
        ),
        media_type="text/event-stream"
    )


@app.post("/createThread")
async def create_thread():
    client = OpenAI()
    my_thread = client.beta.threads.create()
    chroma_conversation_id = uuid.uuid4()
    return {
        "thread_id": my_thread.id,
        "chroma_conversation_id": chroma_conversation_id
    }


@app.post("/setupGptAssistant")
async def setup_gpt_assistant(request: dict = Body(...)):
    assistant_name = request["assistant_properties"]["assistant_name"]
    assistant_instructions = request["assistant_properties"]["assistant_instructions"]
    gpt_model = request["assistant_properties"]["gpt-model"]
    temperature = request["assistant_properties"]["temperature"]

    new_vector_store_name = request["vector_store_properties"]["new_vector_store_name"]
    existing_vector_store_id = request["vector_store_properties"]["existing_vector_store_id"]
    folder_path = request["vector_store_properties"]["folder_path"]
    file_extension = request["vector_store_properties"]["file_extension"]

    documentation_selector = request["documentation_selector"]

    s3_bucket = request["documentation_sources"]["s3"]["s3_bucket"]
    s3_folder_prefix = request["documentation_sources"]["s3"]["s3_folder_prefix"]
    s3_local_folder = request["documentation_sources"]["s3"]["s3_local_folder"]

    setup_outcome = OpenAIAssistantSetup.setup_openai_assistant(
        assistant_name,
        assistant_instructions,
        gpt_model,
        temperature,
        new_vector_store_name,
        existing_vector_store_id,
        folder_path,
        file_extension,
        documentation_selector,
        s3_bucket,
        s3_folder_prefix,
        s3_local_folder
    )
    return {"outcome:": setup_outcome}


def exit_gracefully(signum, frame):
    print(f"Received signal {signum}, saving settings before exit...")
    save_settings_stores()
    exit(0)


signal.signal(signal.SIGTERM, exit_gracefully)
signal.signal(signal.SIGINT, exit_gracefully)

if __name__ == "__main__":
    import uvicorn
    load_settings_stores()
    uvicorn.run(app, host="0.0.0.0", port=8000)
