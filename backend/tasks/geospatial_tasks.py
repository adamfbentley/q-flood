import logging
from celery import shared_task
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.job import Job, JobStatus, SolverType
from backend.core.object_storage import MinioClient
from backend.services.geospatial_processor import GeospatialProcessorService
from backend.tasks.matrix_tasks import generate_matrix_task # Import the next task
import uuid
import os

# Try to import python-magic, fall back to simple file extension checking if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def validate_and_preprocess_task(self, job_id: str, input_data_path: str | None, parameters: dict, solver_type: SolverType):
    logger.info(f"[{job_id}] Celery task 'validate_and_preprocess_task' started.")
    db: Session = SessionLocal()
    job = None
    minio_client = MinioClient()
    geospatial_processor = GeospatialProcessorService()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"[{job_id}] Job not found in DB for geospatial processing. Aborting task.")
            return

        job.status = JobStatus.RUNNING
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"[{job_id}] Job status updated to RUNNING for geospatial processing.")

        if not input_data_path:
            logger.warning(f"[{job_id}] No input_data_path provided. Skipping geospatial validation and pre-processing.")
            # Proceed directly to matrix generation with existing parameters
            generate_matrix_task.delay(job_id, None, parameters, solver_type)
            return

        # 1. Download raw geospatial data
        logger.info(f"[{job_id}] Downloading raw input data from {input_data_path}")
        raw_file_content = minio_client.download_file(input_data_path)
        
        # 2. Robust content type detection using python-magic (if available)
        if MAGIC_AVAILABLE:
            file_type = magic.from_buffer(raw_file_content, mime=True)
            logger.info(f"[{job_id}] Detected file type using python-magic: {file_type}")
        else:
            # Fallback to simple file extension detection
            file_extension = input_data_path.lower().split('.')[-1] if '.' in input_data_path else ''
            file_type_map = {
                'tif': 'image/tiff',
                'tiff': 'image/tiff', 
                'shp': 'application/x-shapefile',
                'json': 'application/json',
                'geojson': 'application/geo+json',
                'txt': 'text/plain'
            }
            file_type = file_type_map.get(file_extension, 'application/octet-stream')
            logger.info(f"[{job_id}] Detected file type from extension: {file_type} (python-magic not available)")
        

        # 3. Validate geospatial data
        logger.info(f"[{job_id}] Validating raw input data.")
        is_valid = geospatial_processor.validate_geospatial_data(raw_file_content, file_type, job_id)
        if not is_valid:
            job.status = JobStatus.VALIDATION_FAILED
            job.fallback_reason = "Geospatial data validation failed."
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.error(f"[{job_id}] Geospatial data validation failed. Job status updated to {job.status}.")
            return # Abort task

        # 4. Pre-process geospatial data
        logger.info(f"[{job_id}] Pre-processing raw input data.")
        preprocessed_content, preprocessed_content_type = geospatial_processor.preprocess_geospatial_data(raw_file_content, file_type, job_id, parameters)

        # 5. Upload pre-processed data to object storage
        preprocessed_object_name = f"jobs/{job_id}/preprocessed_data_{uuid.uuid4()}.json"
        minio_client.upload_file(preprocessed_object_name, preprocessed_content, len(preprocessed_content), preprocessed_content_type)
        logger.info(f"[{job_id}] Pre-processed data saved to {preprocessed_object_name}")

        # 6. Update job with pre-processed data path
        job.preprocessed_data_path = preprocessed_object_name
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"[{job_id}] Job updated with pre-processed data path. Dispatching matrix generation task.")

        # 7. Dispatch the next task in the workflow
        generate_matrix_task.delay(job_id, preprocessed_object_name, parameters, solver_type)

    except Exception as e:
        logger.error(f"[{job_id}] Geospatial processing failed: {e}", exc_info=True)
        if job:
            job.status = JobStatus.PREPROCESSING_FAILED
            job.fallback_reason = f"Geospatial pre-processing failed: {e}"
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"[{job_id}] Job status updated to FAILED due to geospatial processing error.")
        raise # Re-raise to let Celery mark the task as failed
    finally:
        db.close()
