import logging
from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.job import Job, JobStatus, SolverType
from app.services.quantum_solver import QuantumSolverService
from app.tasks.solver_tasks import classical_solve_task # Import classical solver for fallback
from app.tasks.postprocessing_tasks import gis_postprocess_task # Import post-processing task

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def quantum_solve_task(self, job_id: str, matrix_path: str, vector_path: str, parameters: dict, is_fallback_attempt: bool = False):
    log_prefix = f"[{job_id}]"
    logger.info(f"{log_prefix} Celery task 'quantum_solve_task' started.")
    db: Session = SessionLocal()
    job = None # Initialize job to None
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"{log_prefix} Job not found in DB for quantum HHL solve. Aborting task.")
            return

        # Update job status to running for this specific step if it's not already failed
        if job.status != JobStatus.FAILED:
            job.status = JobStatus.RUNNING
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"{log_prefix} Job status updated to RUNNING for quantum HHL solve.")

        quantum_solver = QuantumSolverService()
        solution_path = quantum_solver.solve_hhl(matrix_path, vector_path, job_id, parameters)

        job.solution_path = solution_path
        job.status = JobStatus.COMPLETED # Mark job as completed after successful solve
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"{log_prefix} Quantum HHL solve completed successfully. Solution saved to {solution_path}. Job status updated to COMPLETED.")

        # Dispatch post-processing task
        gis_postprocess_task.delay(job_id, solution_path, parameters)

    except Exception as e:
        logger.error(f"{log_prefix} Quantum HHL solve failed: {e}", exc_info=True)
        if job:
            if job.solver_type == SolverType.HYBRID and not is_fallback_attempt:
                job.status = JobStatus.QUANTUM_FAILED_FALLBACK_INITIATED
                job.fallback_reason = f"Quantum solver failed: {e}. Initiating classical fallback."
                db.add(job)
                db.commit()
                db.refresh(job)
                logger.warning(f"{log_prefix} Quantum solve failed for HYBRID job. Initiating classical fallback.")
                # Dispatch classical fallback task
                classical_solve_task.delay(job_id, matrix_path, vector_path, parameters, is_fallback_attempt=True)
            else:
                job.status = JobStatus.FAILED
                job.fallback_reason = f"Quantum solver failed: {e}"
                db.add(job)
                db.commit()
                db.refresh(job)
                logger.info(f"{log_prefix} Job status updated to FAILED due to quantum HHL solve error.")
        raise # Re-raise to let Celery mark the task as failed
    finally:
        db.close()
