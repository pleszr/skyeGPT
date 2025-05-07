from common import constants
from retriever import db_client
import json


def search_in_skye_documentation(query: str) -> str:
    """Search in Skye documentation. It is a semantic vector database.

  Args:
      query: the question to find the relevant information of
  """
    number_of_results = constants.VECTOR_NUMBER_OF_RESULTS
    collection_name = constants.SKYE_DOC_COLLECTION_NAME
    collection = db_client.get_collection_by_name(collection_name)
    results = collection.query(
        query_texts=[query],
        n_results=number_of_results
    )
    return json.dumps(results)
