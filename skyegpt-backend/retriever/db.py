import chromadb
from chromadb.config import Settings
from common.exceptions import ResponseGenerationError
# Not sure if this is the right way to do it, but with this i was able to run the App
db_client = chromadb.PersistentClient(
    path="./chroma_data",  
    settings=Settings()
)

def delete_collection(collection_name: str):
    try:
        db_client.delete_collection(collection_name)
    except Exception as e:
        raise ResponseGenerationError(f"Collection '{collection_name}' not found") from e

def number_of_documents_in_collection(collection_name: str):
    try:
        collection = db_client.get_collection(collection_name)
        return collection.count()
    except Exception as e:
        raise ResponseGenerationError(f"Collection '{collection_name}' not found") from e

db_client.delete_collection = delete_collection
db_client.number_of_documents_in_collection = number_of_documents_in_collection