import logging
from celery import shared_task
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.job import Job, JobStatus
from backend.models.performance_log import PerformanceLog # New: Import PerformanceLog model
from backend.schemas.performance_log import PerformanceLogCreate # New: Import PerformanceLogCreate schema
from backend.services.classical_solver import ClassicalSolverService
from backend.tasks.postprocessing_tasks import gis_postprocess_task # Import post-processing task

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def classical_solve_task(self, job_id: str, matrix_path: str, vector_path: str, parameters: dict, is_fallback_attempt: bool = False):
    log_prefix = f"[{job_id}] {'[FALLBACK]' if is_fallback_attempt else ''}"
    logger.info(f"{log_prefix} Celery task 'classical_solve_task' started.")
    db: Session = SessionLocal()
    job = None # Initialize job to None
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"{log_prefix} Job not found in DB for classical solve. Aborting task.")
            return

        # Update job status to running for this specific step if it's not already failed
        if job.status not in [JobStatus.FAILED, JobStatus.FALLBACK_CLASSICAL_FAILED]:
            job.status = JobStatus.FALLBACK_CLASSICAL_RUNNING if is_fallback_attempt else JobStatus.RUNNING
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"{log_prefix} Job status updated to {job.status} for classical solve.")

        classical_solver = ClassicalSolverService()
        solution_path, performance_metrics = classical_solver.solve_classical(matrix_path, vector_path, job_id, parameters) # New: Receive metrics

        # Store performance metrics
        performance_log_create = PerformanceLogCreate(
            job_id=job_id,
            step_name=performance_metrics["step_name"],
            execution_time_seconds=performance_metrics["execution_time_seconds"],
            peak_memory_mb=performance_metrics["peak_memory_mb"],
            cpu_utilization_percent=performance_metrics["cpu_utilization_percent"]
        )
        db_performance_log = PerformanceLog(**performance_log_create.model_dump())
        db.add(db_performance_log)
        
        job.solution_path = solution_path
        job.status = JobStatus.FALLBACK_CLASSICAL_COMPLETED if is_fallback_attempt else JobStatus.COMPLETED
        job.latest_performance_metrics = performance_metrics # New: Update latest performance metrics
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"{log_prefix} Classical solve completed successfully. Solution saved to {solution_path}. Job status updated to {job.status}. Performance logged.")

        # Dispatch post-processing task
        gis_postprocess_task.delay(job_id, solution_path, parameters)

    except Exception as e:
        logger.error(f"{log_prefix} Classical solve failed: {e}", exc_info=True)
        if job:
            job.status = JobStatus.FALLBACK_CLASSICAL_FAILED if is_fallback_attempt else JobStatus.FAILED
            job.fallback_reason = f"Classical solve failed: {e}" if is_fallback_attempt else None
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"{log_prefix} Job status updated to {job.status} due to classical solve error.")
        raise # Re-raise to let Celery mark the task as failed
    finally:
        db.close()
