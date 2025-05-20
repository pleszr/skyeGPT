from database import vectordb_client
from typing import List, Dict
import json


def search_in_skye_documentation(query: str) -> List[Dict]:
    """Search in Skye documentation. It is a semantic vector database.

  Args:
      query: the question to find the relevant information of

  Returns:
      List[Dict]: a list of dict which contains the relevant document and the metadata with the
      filename and documentation_link. Example: {
            "document": "# Purpose  \nThis page aims (...) of your application.",
            "metadata": {
              "file_name": "1814692263",
              "documentation_link": "https://sample-url.net/wiki/spaces/IPH/pages/1814692263"
            }
  """
    return vectordb_client.find_related_documents_to_query(query)
