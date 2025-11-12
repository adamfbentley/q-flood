import pytest
import numpy as np
from scipy.sparse import issparse, load_npz
from app.services.matrix_generator import MatrixGeneratorService
import io
import json

def test_generate_laplacian_matrix_2x2():
    service = MatrixGeneratorService()
    A = service._generate_laplacian_matrix(2)
    assert issparse(A)
    assert A.shape == (4, 4)
    expected_A = np.array([
        [4, -1, -1, 0],
        [-1, 4, 0, -1],
        [-1, 0, 4, -1],
        [0, -1, -1, 4]
    ])
    assert np.array_equal(A.toarray(), expected_A)

def test_generate_laplacian_matrix_3x3():
    service = MatrixGeneratorService()
    A = service._generate_laplacian_matrix(3)
    assert issparse(A)
    assert A.shape == (9, 9)
    # Just check a few elements for a larger matrix
    assert A[0, 0] == 4
    assert A[0, 1] == -1
    assert A[0, 3] == -1
    assert A[4, 4] == 4 # Center element
    assert A[4, 3] == -1
    assert A[4, 5] == -1
    assert A[4, 1] == -1
    assert A[4, 7] == -1

def test_read_preprocessed_data_for_grid_resolution_json(mock_minio_client):
    service = MatrixGeneratorService()
    job_id = "test_job_id"
    preprocessed_path = "jobs/test_job_id/preprocessed_data.json"
    mock_minio_client.download_file.return_value = b'{"extracted_parameters": {"grid_resolution": 10}}'
    
    grid_res = service._read_preprocessed_data_for_grid_resolution(preprocessed_path, job_id)
    assert grid_res == 10
    mock_minio_client.download_file.assert_called_with(preprocessed_path)

def test_read_preprocessed_data_for_grid_resolution_invalid(mock_minio_client, caplog):
    service = MatrixGeneratorService()
    job_id = "test_job_id"
    preprocessed_path = "jobs/test_job_id/preprocessed_data.json"
    mock_minio_client.download_file.return_value = b'{"extracted_parameters": {"grid_resolution": "invalid"}}'
    
    with caplog.at_level(20):
        grid_res = service._read_preprocessed_data_for_grid_resolution(preprocessed_path, job_id)
    assert grid_res is None
    assert "Could not extract valid grid_resolution from pre-processed data" in caplog.text

def test_read_preprocessed_data_for_grid_resolution_no_path():
    service = MatrixGeneratorService()
    job_id = "test_job_id"
    grid_res = service._read_preprocessed_data_for_grid_resolution(None, job_id)
    assert grid_res is None

def test_generate_matrix_with_preprocessed_data_priority(mock_minio_client):
    service = MatrixGeneratorService()
    job_id = "test_job_id_1"
    preprocessed_data_path = "jobs/test_job_id_1/preprocessed_data.json"
    parameters = {"grid_resolution": 5}

    mock_minio_client.download_file.return_value = b'{"extracted_parameters": {"grid_resolution": 10}}' # Pre-processed data specifies 10
    mock_minio_client.upload_file.return_value = None

    matrix_path, vector_path = service.generate_matrix(preprocessed_data_path, job_id, parameters)

    assert matrix_path.startswith(f"jobs/{job_id}/matrix_A_")
    assert vector_path.startswith(f"jobs/{job_id}/vector_b_")

    # Verify upload calls
    assert mock_minio_client.upload_file.call_count == 2

    # Verify the matrix generated used grid_resolution = 10 (from preprocessed_data_path)
    uploaded_matrix_data = mock_minio_client.upload_file.call_args_list[0].args[1].getvalue()
    A = load_npz(io.BytesIO(uploaded_matrix_data))
    assert A.shape == (100, 100) # 10*10

def test_generate_matrix_without_preprocessed_data(mock_minio_client):
    service = MatrixGeneratorService()
    job_id = "test_job_id_2"
    preprocessed_data_path = None
    parameters = {"grid_resolution": 7}

    mock_minio_client.upload_file.return_value = None

    matrix_path, vector_path = service.generate_matrix(preprocessed_data_path, job_id, parameters)

    assert matrix_path.startswith(f"jobs/{job_id}/matrix_A_")
    assert vector_path.startswith(f"jobs/{job_id}/vector_b_")

    # Verify upload calls
    assert mock_minio_client.upload_file.call_count == 2

    # Verify the matrix generated used grid_resolution = 7 (from parameters)
    uploaded_matrix_data = mock_minio_client.upload_file.call_args_list[0].args[1].getvalue()
    A = load_npz(io.BytesIO(uploaded_matrix_data))
    assert A.shape == (49, 49) # 7*7

def test_generate_matrix_invalid_parameters_fallback_to_default(mock_minio_client):
    service = MatrixGeneratorService()
    job_id = "test_job_id_3"
    preprocessed_data_path = None
    parameters = {"grid_resolution": "invalid"}

    mock_minio_client.upload_file.return_value = None

    matrix_path, vector_path = service.generate_matrix(preprocessed_data_path, job_id, parameters)

    # Should fall back to default 50x50 grid
    uploaded_matrix_data = mock_minio_client.upload_file.call_args_list[0].args[1].getvalue()
    A = load_npz(io.BytesIO(uploaded_matrix_data))
    assert A.shape == (2500, 2500) # 50*50 default

def test_generate_matrix_preprocessed_data_invalid_fallback_to_parameters(mock_minio_client):
    service = MatrixGeneratorService()
    job_id = "test_job_id_4"
    preprocessed_data_path = "jobs/test_job_id_4/preprocessed_data.json"
    parameters = {"grid_resolution": 15}

    mock_minio_client.download_file.return_value = b'{"extracted_parameters": {"grid_resolution": "not_a_number"}}'
    mock_minio_client.upload_file.return_value = None

    matrix_path, vector_path = service.generate_matrix(preprocessed_data_path, job_id, parameters)

    # Should fall back to parameters grid_resolution = 15
    uploaded_matrix_data = mock_minio_client.upload_file.call_args_list[0].args[1].getvalue()
    A = load_npz(io.BytesIO(uploaded_matrix_data))
    assert A.shape == (225, 225) # 15*15
