import logging
from celery import shared_task
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.job import Job, JobStatus
from backend.services.gis_postprocessor import GISPostProcessorService

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def gis_postprocess_task(self, job_id: str, solution_path: str, parameters: dict):
    logger.info(f"[{job_id}] Celery task 'gis_postprocess_task' started.")
    db: Session = SessionLocal()
    job = None # Initialize job to None
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"[{job_id}] Job not found in DB for GIS post-processing. Aborting task.")
            return

        # Only update status if the job is not already marked as failed from a previous step
        if job.status not in [JobStatus.FAILED, JobStatus.FALLBACK_CLASSICAL_FAILED]:
            # If it's a fallback job, maintain its specific status until post-processing is done
            if job.status == JobStatus.FALLBACK_CLASSICAL_COMPLETED:
                # Keep this status, it will be overwritten by final COMPLETED
                pass
            else:
                job.status = JobStatus.RUNNING # General running status for post-processing
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"[{job_id}] Job status updated to RUNNING for GIS post-processing.")

        gis_processor = GISPostProcessorService()
        geojson_path, pdf_report_path = gis_processor.postprocess_solution(solution_path, job_id, parameters)

        job.geojson_path = geojson_path
        job.pdf_report_path = pdf_report_path
        # Final status update: if it was a fallback, it's now completed via fallback
        if job.status == JobStatus.FALLBACK_CLASSICAL_COMPLETED:
            job.status = JobStatus.FALLBACK_CLASSICAL_COMPLETED # Keep the specific fallback completed status
        else:
            job.status = JobStatus.COMPLETED # Mark job as completed after successful post-processing
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"[{job_id}] GIS post-processing completed successfully. GeoJSON saved to {geojson_path}, PDF to {pdf_report_path}. Job status updated to {job.status}.")

    except Exception as e:
        logger.error(f"[{job_id}] GIS post-processing failed: {e}", exc_info=True)
        if job:
            # If it's a fallback job, mark fallback failed
            if job.status == JobStatus.FALLBACK_CLASSICAL_COMPLETED:
                job.status = JobStatus.FALLBACK_CLASSICAL_FAILED
                job.fallback_reason = f"GIS post-processing failed during fallback: {e}"
            else:
                job.status = JobStatus.FAILED
                job.fallback_reason = f"GIS post-processing failed: {e}"
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"[{job_id}] Job status updated to {job.status} due to GIS post-processing error.")
        raise # Re-raise to let Celery mark the task as failed
    finally:
        db.close()
