import logging
import numpy as np
from scipy.sparse import load_npz
from scipy.sparse.linalg import spsolve
from backend.core.object_storage import MinioClient
import io
import uuid
import time
import psutil
import os

logger = logging.getLogger(__name__)

class ClassicalSolverService:
    def __init__(self):
        self.minio_client = MinioClient()

    def solve_classical(self, matrix_path: str, vector_path: str, job_id: str, parameters: dict) -> tuple[str, dict]:
        """
        Loads matrix A and vector b, solves the linear system Ax=b using a classical solver,
        and stores the solution vector x (pressure field). Captures performance metrics.
        """
        logger.info(f"[{job_id}] Starting classical solve for matrix: {matrix_path}, vector: {vector_path}")

        # Initialize performance metrics
        performance_metrics = {
            "step_name": "classical_solve",
            "execution_time_seconds": 0.0,
            "peak_memory_mb": 0.0,
            "cpu_utilization_percent": 0.0
        }

        # Download A and b from object storage
        matrix_data = self.minio_client.download_file(matrix_path)
        vector_data = self.minio_client.download_file(vector_path)

        A = load_npz(io.BytesIO(matrix_data))
        b = np.load(io.BytesIO(vector_data))

        logger.info(f"[{job_id}] Loaded matrix A (shape: {A.shape}) and vector b (shape: {b.shape}).")

        # Capture performance metrics before solve
        process = psutil.Process(os.getpid())
        mem_before_rss = process.memory_info().rss
        cpu_percent_start = process.cpu_percent(interval=None) # Non-blocking call
        start_time = time.perf_counter()

        # Perform classical solve
        try:
            logger.info(f"[{job_id}] Solving linear system Ax=b using scipy.sparse.linalg.spsolve...")
            x = spsolve(A, b)
            logger.info(f"[{job_id}] Classical solve completed.")
        except Exception as e:
            logger.error(f"[{job_id}] Error during classical solve: {e}", exc_info=True)
            raise

        # Capture performance metrics after solve
        end_time = time.perf_counter()
        mem_after_rss = process.memory_info().rss
        cpu_percent_end = process.cpu_percent(interval=None) # Non-blocking call

        performance_metrics["execution_time_seconds"] = end_time - start_time
        # Approximate peak memory during the operation. More accurate would require sampling.
        performance_metrics["peak_memory_mb"] = (mem_after_rss - mem_before_rss) / (1024 * 1024)
        # CPU utilization over the interval since the last call to cpu_percent
        # If interval=None, it returns the CPU usage since the last call, or 0.0 if first call.
        # For a single operation, it's a snapshot. For more accurate, need to sample over time.
        performance_metrics["cpu_utilization_percent"] = cpu_percent_end

        logger.info(f"[{job_id}] Classical solve performance: {performance_metrics}")

        # Store the solution vector x
        solution_object_name = f"jobs/{job_id}/solution_x_{uuid.uuid4()}.npy"
        with io.BytesIO() as bio_x:
            np.save(bio_x, x)
            bio_x.seek(0)
            self.minio_client.upload_file(solution_object_name, bio_x, bio_x.getbuffer().nbytes, "application/octet-stream")
        logger.info(f"[{job_id}] Solution vector x saved to {solution_object_name}")

        return solution_object_name, performance_metrics
