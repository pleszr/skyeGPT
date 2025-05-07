from ..utils import confluence_2_text
from common import utils, constants
from typing import Any

CONFLUENCE_API_ENDPOINT = "https://innoveo.atlassian.net/wiki/rest/api/content"
CONFLUENCE_SPACE_KEY = "IPH"
CONFLUENCE_SAVE_PATH = constants.IPH_LOCAL_FOLDER_LOCATION


def download_innoveo_partner_hub() -> dict[str, Any]:
    """Downloads the content of IPH confluence space to a local folder and returns
    the local folder structure as a dictionary.

    Returns:
        dict: A nested dictionary representing the local folder tree structure with
        folders and files, suitable for JSON serialization.
    """
    confluence_2_text.download_public_confluence_as_text(
        CONFLUENCE_API_ENDPOINT,
        CONFLUENCE_SPACE_KEY,
        CONFLUENCE_SAVE_PATH
    )
    return utils.folder_to_dict(CONFLUENCE_SAVE_PATH)
