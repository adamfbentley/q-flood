import logging
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from minio.error import S3Error
from backend.core.object_storage import MinioClient
from backend.dependencies import get_api_key
from backend.models.api_key import APIKey

router = APIRouter(tags=["Data Ingestion"])
logger = logging.getLogger(__name__)

@router.post("/upload-geospatial-data")
async def upload_geospatial_data(
    file: UploadFile = File(..., description="Geospatial data file (e.g., GeoTIFF, NetCDF, SHP, CSV)"),
    api_key: APIKey = Depends(get_api_key)
):
    """Uploads a geospatial data file to object storage and returns its path."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided.")

    minio_client = MinioClient()
    try:
        # SEC-002 & CQ-002: Sanitize filename and generate unique object name
        original_filename = os.path.basename(file.filename)
        unique_id = uuid.uuid4()
        object_name = f"raw-inputs/{unique_id}-{original_filename}"

        # SEC-003: Implement streaming upload
        # file.file is a SpooledTemporaryFile, which is a file-like object
        # Minio's put_object can take a file-like object directly.
        if file.size is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not determine file size for upload.")

        minio_client.upload_file(object_name, file.file, file.size, file.content_type)
        logger.info(f"File '{original_filename}' uploaded successfully as '{object_name}'.")
        return {"message": "File uploaded successfully", "object_path": object_name}
    except S3Error as e: # CQ-005: Specific exception for MinIO errors
        logger.error(f"MinIO S3Error during file upload: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to object storage: {e}")
    except Exception as e: # CQ-005: Catch other unexpected errors
        logger.error(f"An unexpected error occurred during file upload: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
