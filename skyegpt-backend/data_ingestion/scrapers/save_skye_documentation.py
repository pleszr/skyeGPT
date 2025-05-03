from ..utils import import_from_S3
from common import utils, constants

S3_BUCKET = "skyedoc"
S3_FOLDER_PREFIX_TEMPLATE = "skye-{{skye_major_version}}.0/"
S3_LOCAL_FOLDER_TEMPLATE = constants.SKYE_DOC_LOCAL_FOLDER_LOCATION_TEMPLATE


def download_skye_documentation_from_s3(skye_major_version: str):
    """
    Downloads Skye documentation files from the S3 bucket to a local folder and returns
    the local folder structure as a dictionary.

    Args:
        skye_major_version (str): The major version of Skye (format: "X.Y", e.g., "9.16")

    Returns:
        dict: A nested dictionary representing the local folder tree structure with
        folders and files, suitable for JSON serialization.
    """
    s3_folder_prefix = utils.replace_placeholders(S3_FOLDER_PREFIX_TEMPLATE, {"skye_major_version": skye_major_version})
    s3_local_folder = utils.generate_local_folder_path_from_skye_version(skye_major_version)
    import_from_S3.download_files_from_s3_bucket(
        S3_BUCKET,
        s3_folder_prefix,
        s3_local_folder
    )
    return utils.folder_to_dict(s3_local_folder)
