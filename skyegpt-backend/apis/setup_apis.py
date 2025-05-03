from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import Response
from common import logger
from dependencies import get_ingestion_service, get_database_service
from services.setup_services import IngestionService, DatabaseService
from exceptions import CollectionNotFoundError
from .schemas.requests import SkyeVersionRequest, ImportRequest
from .schemas.responses import DownloadResponse, ImportResponse
from common.decorators import catch_unknown_errors
from common import message_bundle, constants


setup_apis_router = APIRouter(prefix="/setup", tags=["Setup Endpoints"])


@setup_apis_router.post("/data/skye-documentation",
                        summary="Download Skye documentation to server",
                        description=(
                                """Downloads the documentation of a given version to the server, 
                                returns the tree structure of the folder."""
                        ),
                        responses={
                            200: {"description": "Documentation downloaded successfully to the server."},
                            400: {"description": "Version does not exist in S3 bucket."},
                            500: {"description": "Internal server error."}
                        },
                        status_code=status.HTTP_200_OK)
@catch_unknown_errors
async def download_skye_documentation(
        request: SkyeVersionRequest,
        ingestion_service: IngestionService = Depends(get_ingestion_service)
) -> DownloadResponse:
    skye_major_version = request.skye_major_version
    try:
        tree_structure = ingestion_service.download_skye_documentation_to_server(skye_major_version)
        return DownloadResponse(folder_content=tree_structure)
    except FileNotFoundError as file_not_found_error:
        error_message = f"Version {skye_major_version} does not exist in S3 bucket"
        logger.info(error_message, error=file_not_found_error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)


@setup_apis_router.post("/data/innoveo-partner-hub",
                        summary="Download Innoveo Partner Hub to server",
                        description=(
                                "Downloads the content of Innoveo Partner Hub (IPH) from confluence to the server"
                        ),
                        responses={
                            200: {"description": "Documentation downloaded successfully to the server."},
                            500: {"description": "Internal server error."}
                        },
                        status_code=status.HTTP_200_OK)
@catch_unknown_errors
async def download_iph(
        ingestion_service: IngestionService = Depends(get_ingestion_service)
) -> DownloadResponse:
    tree_structure = ingestion_service.download_iph_to_server()
    return DownloadResponse(folder_content=tree_structure)


@setup_apis_router.delete(
    "/database/collections/{collection_name}",
    summary="Deletes a collection from the database.",
    description="Deletes a collection based on the name of the collection.",
    responses={
        204: {"description": "Collection deleted successfully."},
        404: {"description": "Collection not found."},
        500: {"description": "Internal server error."}
    },
    status_code=204,
    response_class=Response
)
@catch_unknown_errors
async def delete_collection(collection_name: str, db_service: DatabaseService = Depends(get_database_service)):
    try:
        db_service.delete_collection(collection_name)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except CollectionNotFoundError as value_error:
        error_message = f"Tried to delete {collection_name}, but it doesn't exist"
        logger.info(error_message, error=value_error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)


@setup_apis_router.post("/import",
                        summary="Import downloaded content to Vector database",
                        description=(
                                """Imports the previously downloaded content to vector database where the 
                                retriever will fetch it from to give context to the AI agents"""
                        ),
                        responses={
                            200: {"description": "Import successful. Returns the number of all imported documents."},
                            500: {"description": message_bundle.INTERNAL_ERROR},
                            422: {"description": "Incorrect request"}
                        },
                        status_code=status.HTTP_200_OK)
@catch_unknown_errors
async def import_to_database(
        request: ImportRequest,
        ingestion_service: IngestionService = Depends(get_ingestion_service),
        database_service: DatabaseService = Depends(get_database_service)
) -> ImportResponse:
    markdown_split_headers = request.markdown_split_headers

    should_import_skyedoc: bool = request.imports.skyedoc.enabled
    if should_import_skyedoc:
        logger.info('Starting to import skyedoc')
        skye_major_version = request.imports.skyedoc.skye_major_version
        ingestion_service.import_skyedoc(skye_major_version, markdown_split_headers)

    should_import_iph: bool = request.imports.innoveo_partner_hub.enabled
    if should_import_iph:
        logger.info('Starting to import IPH')
        ingestion_service.import_iph(markdown_split_headers)

    if not should_import_skyedoc and not should_import_iph:
        logger.warning(message_bundle.NO_IMPORT_SELECTED)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message_bundle.NO_IMPORT_SELECTED)

    number_of_documents = database_service.number_of_documents_in_collection(constants.SKYE_DOC_COLLECTION_NAME)
    return ImportResponse(number_of_documents=number_of_documents)
