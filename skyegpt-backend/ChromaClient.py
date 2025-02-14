import chromadb
from datetime import datetime

chroma_client = chromadb.PersistentClient()


def create_collection_if_needed(
        collection_name: str
):
    chroma_client.get_or_create_collection(collection_name,
                                           metadata={
                                               "description": "ChromaDB for GPT purposes",
                                               "created": str(datetime.now())
                                           })


def number_of_documents_in_collection(collection_name: str):
    try:
        collection = chroma_client.get_collection(collection_name)
        return collection.count()
    except chromadb.errors.InvalidCollectionException:
        print(f"Collection with name {collection_name} not found. Returning 0 as number of documents")
        return 0


def get_collection_by_name(collection_name: str):
    try:
        return chroma_client.get_collection(name=collection_name)
    except chromadb.errors.InvalidCollectionException:
        print(f"Error: Collection with name {collection_name} not found.")
        return None


def create_collection(collection_name: str):
    return chroma_client.create_collection(
        name=collection_name,
        metadata={
            "description": "ChromaDB for GPT purposes",
            "created": str(datetime.now())
        }
    )


def delete_collection(collection_name: str):
    chroma_client.delete_collection(name=collection_name)


def add_to_collection(
        collection,
        documents,
        metadatas,
        ids
):
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )


def verify_if_collection_exists(
        collection_name: str
) -> bool:
    if get_collection_by_name(collection_name):
        return True
    else:
        return False


def set_chroma_client(
        client
):
    global chroma_client
    chroma_client = client

