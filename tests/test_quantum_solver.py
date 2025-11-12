import pytest
import numpy as np
from scipy.sparse import save_npz, csr_matrix
from app.services.quantum_solver import QuantumSolverService
import io
from unittest.mock import MagicMock
import qiskit.algorithms.linear_solvers # Import the module to access HHL directly

# Mock Qiskit HHL and AerSimulator for isolated testing
@pytest.fixture(autouse=True)
def mock_qiskit(mocker):
    mocker.patch('qiskit_aer.AerSimulator', autospec=True)
    mock_hhl_instance = MagicMock()
    
    # Mock Statevector object
    mock_statevector = MagicMock()
    # For a 4x4 HHL, the solution register would typically be 2 qubits, leading to a 4-element statevector.
    # Let's assume a simple 4-element solution vector for the 4x4 system.
    mock_statevector.data = np.array([0.1, 0.2, 0.3, 0.4]) # Example real-valued solution amplitudes
    
    mock_hhl_instance.solve.return_value.state_solution = mock_statevector
    mocker.patch('qiskit.algorithms.linear_solvers.HHL', return_value=mock_hhl_instance)

# Helper to create dummy sparse matrix and vector
def create_dummy_sparse_data(dim: int, is_ill_conditioned: bool = False):
    if dim == 2:
        A_dense = np.array([[1, -0.5], [-0.5, 1]])
        b_vec = np.array([0, 1])
    elif dim == 4:
        A_dense = np.array([
            [4, -1, 0, -1],
            [-1, 4, -1, 0],
            [0, -1, 4, -1],
            [-1, 0, -1, 4]
        ]) # A 2x2 Laplacian matrix (N=4)
        if is_ill_conditioned:
            # Make it ill-conditioned by making rows/cols linearly dependent
            A_dense[0,:] = A_dense[1,:] # Make row 0 same as row 1
            A_dense[:,0] = A_dense[:,1] # Make col 0 same as col 1
        b_vec = np.array([0.1, 0.1, 0.1, 0.1])
    else:
        # For larger dimensions, create a simple tridiagonal matrix for testing structure
        A_dense = np.diag(np.ones(dim) * 2) + np.diag(np.ones(dim-1) * -1, k=1) + np.diag(np.ones(dim-1) * -1, k=-1)
        b_vec = np.ones(dim) * 0.1

    A_sparse = csr_matrix(A_dense)

    matrix_bio = io.BytesIO()
    save_npz(matrix_bio, A_sparse)
    matrix_bio.seek(0)

    vector_bio = io.BytesIO()
    np.save(vector_bio, b_vec)
    vector_bio.seek(0)

    return matrix_bio.getvalue(), vector_bio.getvalue(), A_dense, b_vec

def test_solve_hhl_with_4x4_input_uses_actual_matrix(mock_minio_client, caplog):
    service = QuantumSolverService()
    job_id = "test_job_id_hhl_4x4"
    parameters = {}

    matrix_data, vector_data, A_expected, b_expected = create_dummy_sparse_data(4)

    mock_minio_client.download_file.side_effect = [matrix_data, vector_data]
    mock_minio_client.upload_file.return_value = None

    with caplog.at_level(20): # INFO level
        solution_path = service.solve_hhl("matrix_path", "vector_path", job_id, parameters)

    assert solution_path.startswith(f"jobs/{job_id}/solution_x_quantum_")
    mock_minio_client.download_file.assert_called_with("vector_path")
    mock_minio_client.upload_file.assert_called_once()

    # Verify that the HHL solver was called with the actual 4x4 matrix
    hhl_mock = qiskit.algorithms.linear_solvers.HHL.return_value
    hhl_mock.solve.assert_called_once()
    args, _ = hhl_mock.solve.call_args
    passed_matrix = args[0]
    passed_vector = args[1]

    np.testing.assert_array_almost_equal(passed_matrix, A_expected)
    # The vector passed to HHL is normalized, so compare normalized
    np.testing.assert_array_almost_equal(passed_vector, b_expected / np.linalg.norm(b_expected))

    assert "Using 4x4 submatrix of input A and subvector of b for HHL demonstration." in caplog.text
    assert "Input matrix A is smaller than the target HHL dimension" not in caplog.text
    assert "Extracted HHL matrix is not symmetric" not in caplog.text
    assert "Extracted HHL matrix is ill-conditioned" not in caplog.text

def test_solve_hhl_with_larger_input_truncates_and_logs_warning(mock_minio_client, caplog):
    service = QuantumSolverService()
    job_id = "test_job_id_hhl_larger"
    parameters = {}

    matrix_data, vector_data, _, _ = create_dummy_sparse_data(9) # 9x9 matrix

    mock_minio_client.download_file.side_effect = [matrix_data, vector_data]
    mock_minio_client.upload_file.return_value = None

    with caplog.at_level(20): # INFO level
        solution_path = service.solve_hhl("matrix_path", "vector_path", job_id, parameters)

    assert solution_path.startswith(f"jobs/{job_id}/solution_x_quantum_")
    mock_minio_client.download_file.assert_called_with("vector_path")
    mock_minio_client.upload_file.assert_called_once()

    # Verify that the HHL solver was called with a 4x4 submatrix
    hhl_mock = qiskit.algorithms.linear_solvers.HHL.return_value
    hhl_mock.solve.assert_called_once()
    args, _ = hhl_mock.solve.call_args
    passed_matrix = args[0]
    passed_vector = args[1]

    # Expect a 4x4 submatrix of the 9x9 input
    expected_A_sub = csr_matrix(create_dummy_sparse_data(9)[2][:4, :4]).toarray()
    expected_b_sub = create_dummy_sparse_data(9)[3][:4]

    np.testing.assert_array_almost_equal(passed_matrix, expected_A_sub)
    np.testing.assert_array_almost_equal(passed_vector, expected_b_sub / np.linalg.norm(expected_b_sub))

    assert "Using 4x4 submatrix of input A and subvector of b for HHL demonstration." in caplog.text
    assert "Input matrix A (shape: (9, 9)) is smaller than the target HHL dimension" not in caplog.text
    assert "Extracted HHL matrix is not symmetric" not in caplog.text
    assert "Extracted HHL matrix is ill-conditioned" not in caplog.text

def test_solve_hhl_with_smaller_input_uses_default_and_logs_warning(mock_minio_client, caplog):
    service = QuantumSolverService()
    job_id = "test_job_id_hhl_smaller"
    parameters = {}

    matrix_data, vector_data, _, _ = create_dummy_sparse_data(2) # 2x2 matrix

    mock_minio_client.download_file.side_effect = [matrix_data, vector_data]
    mock_minio_client.upload_file.return_value = None

    with caplog.at_level(20): # INFO level
        solution_path = service.solve_hhl("matrix_path", "vector_path", job_id, parameters)

    assert solution_path.startswith(f"jobs/{job_id}/solution_x_quantum_")
    mock_minio_client.download_file.assert_called_with("vector_path")
    mock_minio_client.upload_file.assert_called_once()

    # Verify that the HHL solver was called with the default 4x4 matrix
    hhl_mock = qiskit.algorithms.linear_solvers.HHL.return_value
    hhl_mock.solve.assert_called_once()
    args, _ = hhl_mock.solve.call_args
    passed_matrix = args[0]
    passed_vector = args[1]

    expected_default_A = np.array([[1, -0.5, 0, 0], [-0.5, 1, -0.5, 0], [0, -0.5, 1, -0.5], [0, 0, -0.5, 1]])
    expected_default_b = np.array([0, 1, 0, 1])

    np.testing.assert_array_almost_equal(passed_matrix, expected_default_A)
    np.testing.assert_array_almost_equal(passed_vector, expected_default_b / np.linalg.norm(expected_default_b))

    assert "Input matrix A (shape: (2, 2)) is smaller than the target HHL dimension (4x4). Using a default well-conditioned 4x4 matrix for HHL demonstration." in caplog.text

def test_solve_hhl_with_non_square_input_raises_error(mock_minio_client, caplog):
    service = QuantumSolverService()
    job_id = "test_job_id_non_square"
    parameters = {}

    # Create a non-square sparse matrix
    A_non_square = csr_matrix(np.array([[1, 2, 3], [4, 5, 6]]))
    b_vec = np.array([1, 2])

    matrix_bio = io.BytesIO()
    save_npz(matrix_bio, A_non_square)
    matrix_bio.seek(0)

    vector_bio = io.BytesIO()
    np.save(vector_bio, b_vec)
    vector_bio.seek(0)

    mock_minio_client.download_file.side_effect = [matrix_bio.getvalue(), vector_bio.getvalue()]
    mock_minio_client.upload_file.return_value = None

    with pytest.raises(ValueError, match="Input matrix A must be square"): # Updated error message
        service.solve_hhl("matrix_path", "vector_path", job_id, parameters)

    assert "Input matrix A must be square, but has shape (2, 3)." in caplog.text
    assert qiskit.algorithms.linear_solvers.HHL.return_value.solve.call_count == 0

def test_solve_hhl_with_ill_conditioned_input_uses_default_and_logs_warning(mock_minio_client, caplog):
    service = QuantumSolverService()
    job_id = "test_job_id_ill_conditioned"
    parameters = {}

    matrix_data, vector_data, _, _ = create_dummy_sparse_data(4, is_ill_conditioned=True)

    mock_minio_client.download_file.side_effect = [matrix_data, vector_data]
    mock_minio_client.upload_file.return_value = None

    with caplog.at_level(20): # INFO level
        solution_path = service.solve_hhl("matrix_path", "vector_path", job_id, parameters)

    assert solution_path.startswith(f"jobs/{job_id}/solution_x_quantum_")
    mock_minio_client.download_file.assert_called_with("vector_path")
    mock_minio_client.upload_file.assert_called_once()

    # Verify that the HHL solver was called with the default 4x4 matrix
    hhl_mock = qiskit.algorithms.linear_solvers.HHL.return_value
    hhl_mock.solve.assert_called_once()
    args, _ = hhl_mock.solve.call_args
    passed_matrix = args[0]
    passed_vector = args[1]

    expected_default_A = np.array([[1, -0.5, 0, 0], [-0.5, 1, -0.5, 0], [0, -0.5, 1, -0.5], [0, 0, -0.5, 1]])
    expected_default_b = np.array([0, 1, 0, 1])

    np.testing.assert_array_almost_equal(passed_matrix, expected_default_A)
    np.testing.assert_array_almost_equal(passed_vector, expected_default_b / np.linalg.norm(expected_default_b))

    assert "Extracted HHL matrix is ill-conditioned" in caplog.text
    assert "Using a default well-conditioned 4x4 matrix." in caplog.text

def test_solve_hhl_uploads_solution(mock_minio_client, mock_qiskit):
    service = QuantumSolverService()
    job_id = "test_job_id_upload"
    parameters = {}

    matrix_data, vector_data, _, _ = create_dummy_sparse_data(4)

    mock_minio_client.download_file.side_effect = [matrix_data, vector_data]
    mock_minio_client.upload_file.return_value = None

    service.solve_hhl("matrix_path", "vector_path", job_id, parameters)

    # Verify that upload_file was called with the correct content type and data
    call_args = mock_minio_client.upload_file.call_args
    assert call_args is not None
    assert call_args.args[3] == "application/octet-stream"
    uploaded_data = np.load(io.BytesIO(call_args.args[1].getvalue()))
    
    # The mock_qiskit fixture returns a fixed state_solution.data = np.array([0.1, 0.2, 0.3, 0.4])
    # The b_norm for the default b_hhl_vector = np.array([0, 1, 0, 1]) is sqrt(2)
    # So x_extracted = [0.1, 0.2, 0.3, 0.4] * sqrt(2)
    # This test primarily checks if *something* was uploaded, not the exact HHL math, as HHL is mocked.
    # The b_norm used for scaling back is derived from the vector actually passed to HHL. For the 4x4 case, it's b_expected.
    _, _, _, b_expected_for_4x4 = create_dummy_sparse_data(4)
    expected_x_extracted = np.array([0.1, 0.2, 0.3, 0.4]) * np.linalg.norm(b_expected_for_4x4)
    np.testing.assert_array_almost_equal(uploaded_data, expected_x_extracted)

def test_solve_hhl_with_zero_vector_raises_error(mock_minio_client, caplog):
    service = QuantumSolverService()
    job_id = "test_job_id_zero_vector"
    parameters = {}

    A_4x4 = csr_matrix(np.array([
        [4, -1, 0, -1],
        [-1, 4, -1, 0],
        [0, -1, 4, -1],
        [-1, 0, -1, 4]
    ]))
    b_zero = np.array([0, 0, 0, 0])

    matrix_bio = io.BytesIO()
    save_npz(matrix_bio, A_4x4)
    matrix_bio.seek(0)

    vector_bio = io.BytesIO()
    np.save(vector_bio, b_zero)
    vector_bio.seek(0)

    mock_minio_client.download_file.side_effect = [matrix_bio.getvalue(), vector_bio.getvalue()]
    mock_minio_client.upload_file.return_value = None

    with pytest.raises(ValueError, match="Vector b cannot be a zero vector for HHL."): # Updated error message
        service.solve_hhl("matrix_path", "vector_path", job_id, parameters)
    
    assert "Vector b cannot be a zero vector for HHL." in caplog.text
    assert qiskit.algorithms.linear_solvers.HHL.return_value.solve.call_count == 0
