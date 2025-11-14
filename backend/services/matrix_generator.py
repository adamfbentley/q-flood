import logging
import numpy as np
from scipy.sparse import lil_matrix, save_npz
from backend.core.object_storage import MinioClient
import io
import uuid
import json

logger = logging.getLogger(__name__)

class MatrixGeneratorService:
    def __init__(self):
        self.minio_client = MinioClient()

    def _generate_laplacian_matrix(self, grid_resolution: int):
        """
        Generates a sparse 2D Laplacian matrix for a grid_resolution x grid_resolution grid.
        This is a simplified representation for a flood model, often used in finite difference methods.
        """
        N = grid_resolution * grid_resolution
        A = lil_matrix((N, N))

        for i in range(grid_resolution):
            for j in range(grid_resolution):
                idx = i * grid_resolution + j

                # Diagonal element
                A[idx, idx] = 4 # Represents -4 * u_ij in a discretized Laplacian

                # Neighbors
                if i > 0: A[idx, idx - grid_resolution] = -1 # u_{i-1, j}
                if i < grid_resolution - 1: A[idx, idx + grid_resolution] = -1 # u_{i+1, j}
                if j > 0: A[idx, idx - 1] = -1 # u_{i, j-1}
                if j < grid_resolution - 1: A[idx, idx + 1] = -1 # u_{i, j+1}
        return A.tocsr()

    def _read_preprocessed_data_for_grid_resolution(self, preprocessed_data_path: str, job_id: str) -> int | None:
        """
        Reads pre-processed geospatial data from object storage to extract grid_resolution.
        Assumes the pre-processed data is a JSON string containing metadata.
        """
        if not preprocessed_data_path:
            return None

        try:
            logger.info(f"[{job_id}] Attempting to read grid_resolution from preprocessed_data_path: {preprocessed_data_path}")
            file_content = self.minio_client.download_file(preprocessed_data_path).decode('utf-8')
            
            data = json.loads(file_content)
            if 'extracted_parameters' in data and 'grid_resolution' in data['extracted_parameters'] and isinstance(data['extracted_parameters']['grid_resolution'], int):
                logger.info(f"[{job_id}] Extracted grid_resolution {data['extracted_parameters']['grid_resolution']} from pre-processed data.")
                return data['extracted_parameters']['grid_resolution']
            
            logger.warning(f"[{job_id}] Could not extract valid grid_resolution from pre-processed data '{preprocessed_data_path}'. Content: '{file_content[:50]}...'")
            return None
        except Exception as e:
            logger.warning(f"[{job_id}] Failed to download or process preprocessed_data_path '{preprocessed_data_path}' for grid_resolution: {e}")
            return None

    def generate_matrix(self, preprocessed_data_path: str | None, job_id: str, parameters: dict) -> tuple[str, str]:
        """
        Generates the sparse matrix A and right-hand side vector b for a flood simulation job.

        This method now prioritizes `grid_resolution` from `preprocessed_data_path` if available and valid,
        falling back to the `parameters` dictionary if not.
        """
        logger.info(f"[{job_id}] Starting matrix generation.")

        grid_resolution_from_preprocessed = self._read_preprocessed_data_for_grid_resolution(preprocessed_data_path, job_id)
        
        grid_resolution = parameters.get("grid_resolution", 50) # Default if not in parameters

        if grid_resolution_from_preprocessed is not None and grid_resolution_from_preprocessed > 0:
            grid_resolution = grid_resolution_from_preprocessed
            logger.info(f"[{job_id}] Using grid_resolution {grid_resolution} from pre-processed data.")
        elif not isinstance(grid_resolution, int) or grid_resolution <= 0:
            logger.warning(f"[{job_id}] Invalid grid_resolution in parameters ({parameters.get('grid_resolution')}). Falling back to default 50.")
            grid_resolution = 50 # Fallback to a safe default
        else:
            logger.info(f"[{job_id}] Using grid_resolution {grid_resolution} from job parameters.")

        # Generate a simple 2D Laplacian matrix
        A = self._generate_laplacian_matrix(grid_resolution)

        # Generate a synthetic right-hand side vector b
        # For a flood model, b might represent sources/sinks or boundary conditions
        b = np.ones(A.shape[0]) * 0.1 # Example: uniform source term

        # Save A and b to object storage
        matrix_object_name = f"jobs/{job_id}/matrix_A_{uuid.uuid4()}.npz"
        vector_object_name = f"jobs/{job_id}/vector_b_{uuid.uuid4()}.npy"

        # Save A
        with io.BytesIO() as bio_a:
            save_npz(bio_a, A)
            bio_a.seek(0)
            self.minio_client.upload_file(matrix_object_name, bio_a, bio_a.getbuffer().nbytes, "application/octet-stream")
        logger.info(f"[{job_id}] Matrix A saved to {matrix_object_name}")

        # Save b
        with io.BytesIO() as bio_b:
            np.save(bio_b, b)
            bio_b.seek(0)
            self.minio_client.upload_file(vector_object_name, bio_b, bio_b.getbuffer().nbytes, "application/octet-stream")
        logger.info(f"[{job_id}] Vector b saved to {vector_object_name}")

        return matrix_object_name, vector_object_name
