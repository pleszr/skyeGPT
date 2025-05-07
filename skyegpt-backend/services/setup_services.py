from data_ingestion.scrapers.save_skye_documentation import download_skye_documentation_from_s3
from data_ingestion.scrapers.save_innoveo_partner_hub import download_innoveo_partner_hub
from common import logger, utils, constants
from retriever import db_client
from common.exceptions import ResponseGenerationError
from data_ingestion.persister import markdown_2_vector_db


class IngestionService:
    """
    Service responsible for handling data-ingestion related operations.
    """
    def download_skye_documentation_to_server(self, version: str) -> dict:
        """
        Orchestrates the downloading of Skye documentation to the server.

        Args:
            version (str): The major version string (e.g., "10.0").

        Returns:
            dict: The tree structure of the downloaded content as a proof that the download was successful.
            Can be ignored.

        Raises:
            FileNotFoundError: If the specified version doesn't exist in S3.
            Exception: For other potential download errors.
        """
        logger.info(f"IngestionService: Attempting download for version {version}")
        try:
            result = download_skye_documentation_from_s3(version)
            logger.info(f"IngestionService: Download successful for version {version}")
            return result
        except FileNotFoundError as e:
            logger.info(f"IngestionService: Version {version} not found.", exc_info=True)
            raise e
        except Exception as e:
            logger.exception(f"IngestionService: Unexpected error downloading version {version}", exc_info=True)
            raise e

    def download_iph_to_server(self) -> dict:
        """Orchestrates the downloading of Innoveo Partner Hub to the server.

        Returns:
            dict: The tree structure of the downloaded content as a proof that the download was successful.
            Can be ignored.

        Raises:
            TBD
            Exception: For other potential download errors.
        """
        logger.info(f"IngestionService: Attempting to download IPH")
        try:
            result = download_innoveo_partner_hub()
            logger.info(f"IngestionService: Download successful for IPH")
            return result
        except Exception as e:
            logger.exception(f"IngestionService: Unexpected error downloading IPH")
            raise e

    def import_skyedoc(self, skye_major_version: str, markdown_headers: list) -> int:
        """Orchestrates the importing of Skyedoc to the retriever database from local storage.

        Raises:
            TODO add more error handling
            Exception: For yet unknown errors
        """
        logger.info(f"IngestionService: Attempting to import SkyeDoc version {skye_major_version}")
        try:
            skyedoc_folder_path = utils.generate_local_folder_path_from_skye_version(skye_major_version)
            markdown_2_vector_db.scan_and_import_markdowns_from_folder(
                constants.SKYE_DOC_COLLECTION_NAME,
                skyedoc_folder_path,
                markdown_headers
            )
            logger.info(f"Skyedoc for version {skye_major_version} successfully imported")
        except Exception as e:
            logger.exception(f"IngestionService: Unexpected error importing SkyeDoc version ${skye_major_version}")
            raise e

    def import_iph(self, markdown_headers: list) -> None:
        """Orchestrates the importing of Innoveo Partner Hub to the retriever database from local storage.

        Raises:
            TODO add more error handling
            Exception: For yet unknown errors
        """
        logger.info(f"IngestionService: Attempting to import IPH to lookup database")
        try:
            markdown_2_vector_db.scan_and_import_markdowns_from_folder(
                constants.IPH_DOC_COLLECTION_NAME,
                constants.IPH_LOCAL_FOLDER_LOCATION,
                markdown_headers
            )
            logger.info(f"IPH successfully imported")
        except Exception as e:
            logger.exception(f"IngestionService: Unexpected error importing IPH")
            raise e


class DatabaseService:
    """Service responsible for handling database collection operations."""
    def delete_collection(self, collection_name: str):
        """
        Orchestrates the deletion of a database collection.

        Args:
            collection_name (str): The name of the collection to delete.

        Raises:
            CollectionNotFoundError: If the collection does not exist (as raised by ChromaClient).
            Exception: For other potential database errors.
        """
        logger.info(f"DatabaseService: Attempting deletion of collection '{collection_name}'")
        try:
            db_client.delete_collection(collection_name)
            logger.info(f"DatabaseService: Deletion successful for collection '{collection_name}'")
        except ResponseGenerationError as e:
            logger.info(f"DatabaseService: Collection '{collection_name}' not found for deletion.", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"DatabaseService: Unexpected error deleting collection '{collection_name}'", exc_info=True)
            raise e


    def number_of_documents_in_collection(self, collection_name: str):
        """
        Returns the number of documents in a given collection

        Args:
            collection_name (str): The name of the collection to delete.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
            Exception: For other potential database errors.
        """
        logger.info(f"DatabaseService: Attempting to return number of documents of '{collection_name}'")
        try:
            number_of_documents = db_client.number_of_documents_in_collection(collection_name)
            logger.info(f"DatabaseService: Number of collections in {collection_name}: {number_of_documents}")
            return number_of_documents
        except ResponseGenerationError as e:
            logger.exception(f"DatabaseService: Collection '{collection_name}' not found for deletion.")
            raise e
        except Exception as e:
            logger.error(f"DatabaseService: Unexpected error when checking nuber of documents in '{collection_name}'")
            raise e
