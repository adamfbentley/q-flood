import logging
from celery import shared_task
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.job import Job, JobStatus, SolverType
from backend.services.matrix_generator import MatrixGeneratorService
from backend.tasks.solver_tasks import classical_solve_task # Import the classical solver task
from backend.tasks.quantum_tasks import quantum_solve_task # Import the quantum solver task

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_matrix_task(self, job_id: str, preprocessed_data_path: str | None, parameters: dict, solver_type: SolverType):
    logger.info(f"[{job_id}] Celery task 'generate_matrix_task' started.")
    db: Session = SessionLocal()
    job = None # Initialize job to None
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"[{job_id}] Job not found in DB for matrix generation. Aborting task.")
            return

        job.status = JobStatus.RUNNING
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"[{job_id}] Job status updated to RUNNING for matrix generation.")

        matrix_generator = MatrixGeneratorService()
        matrix_path, vector_path = matrix_generator.generate_matrix(preprocessed_data_path, job_id, parameters)

        job.matrix_path = matrix_path
        job.vector_path = vector_path
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"[{job_id}] Matrix and vector paths updated in DB.")

        # Dispatch the appropriate solver task based on job_type
        if solver_type == SolverType.CLASSICAL:
            logger.info(f"[{job_id}] Dispatching classical solve task.")
            classical_solve_task.delay(job_id, matrix_path, vector_path, parameters, is_fallback_attempt=False)
        elif solver_type in [SolverType.QUANTUM, SolverType.HYBRID]:
            logger.info(f"[{job_id}] Dispatching quantum HHL solve task (solver type: {solver_type}).")
            quantum_solve_task.delay(job_id, matrix_path, vector_path, parameters, is_fallback_attempt=False)
        else:
            logger.error(f"[{job_id}] Unknown solver type '{solver_type}'. No solver task dispatched.")
            job.status = JobStatus.FAILED
            db.add(job)
            db.commit()
            db.refresh(job)

    except Exception as e:
        logger.error(f"[{job_id}] Matrix generation failed: {e}", exc_info=True)
        if job:
            job.status = JobStatus.FAILED
            job.fallback_reason = f"Matrix generation failed: {e}"
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"[{job_id}] Job status updated to FAILED due to matrix generation error.")
        raise # Re-raise to let Celery mark the task as failed
    finally:
        db.close()
