import logging
from minio import Minio
from minio.error import S3Error
from backend.core.config import settings
import io

logger = logging.getLogger(__name__)

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.client.make_bucket(settings.MINIO_BUCKET_NAME)
                logger.info(f"Bucket '{settings.MINIO_BUCKET_NAME}' created successfully.") # CQ-005: Use logging
        except S3Error as e: # CQ-005: Specific exception
            logger.error(f"Error checking/creating bucket: {e}", exc_info=True) # CQ-005: Use logging
            raise
        except Exception as e: # CQ-005: Catch other potential errors
            logger.error(f"An unexpected error occurred during bucket check/creation: {e}", exc_info=True)
            raise

    def upload_file(self, object_name: str, file_stream: io.IOBase, file_size: int, content_type: str):
        """Uploads a file stream to the configured MinIO bucket."""
        try:
            self.client.put_object(
                settings.MINIO_BUCKET_NAME,
                object_name,
                file_stream, # SEC-003: Pass the stream directly
                file_size,   # SEC-003: Pass the size
                content_type=content_type
            )
            logger.info(f"'{object_name}' is successfully uploaded to bucket '{settings.MINIO_BUCKET_NAME}'.") # CQ-005: Use logging
        except S3Error as e: # CQ-005: Specific exception
            logger.error(f"Error uploading file '{object_name}': {e}", exc_info=True) # CQ-005: Use logging
            raise
        except Exception as e: # CQ-005: Catch other potential errors during stream processing
            logger.error(f"An unexpected error occurred during file upload '{object_name}': {e}", exc_info=True)
            raise

    def download_file(self, object_name: str) -> bytes:
        """Downloads a file from the configured MinIO bucket."""
        try:
            response = self.client.get_object(settings.MINIO_BUCKET_NAME, object_name)
            return response.read()
        except S3Error as e: # CQ-005: Specific exception
            logger.error(f"Error downloading file '{object_name}': {e}", exc_info=True) # CQ-005: Use logging
            raise
        except Exception as e: # CQ-005: Catch other potential errors
            logger.error(f"An unexpected error occurred during file download '{object_name}': {e}", exc_info=True)
            raise
        finally:
            if 'response' in locals() and response:
                response.close()
                response.release_conn()
