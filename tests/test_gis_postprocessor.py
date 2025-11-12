import pytest
import numpy as np
import geojson
from app.services.gis_postprocessor import GISPostProcessorService
import io
from datetime import datetime

def test_convert_solution_to_flood_depth_basic():
    service = GISPostProcessorService()
    solution_vector = np.array([1.0, 2.0, -0.5, 3.0])
    parameters = {"conversion_factor": 0.5}
    flood_depth = service._convert_solution_to_flood_depth(solution_vector, parameters)
    np.testing.assert_array_almost_equal(flood_depth, [0.5, 1.0, 0.0, 1.5])

def test_convert_solution_to_flood_depth_with_elevation_and_offset():
    service = GISPostProcessorService()
    solution_vector = np.array([1.0, 2.0, 3.0, 4.0])
    parameters = {
        "conversion_factor": 0.5,
        "base_elevation": 0.8,
        "water_level_offset": 0.3
    }
    # Expected: (solution * 0.5) + 0.3 - 0.8
    # [0.5, 1.0, 1.5, 2.0] + 0.3 - 0.8
    # [0.0, 0.5, 1.0, 1.5]
    flood_depth = service._convert_solution_to_flood_depth(solution_vector, parameters)
    np.testing.assert_array_almost_equal(flood_depth, [0.0, 0.5, 1.0, 1.5])

def test_generate_geojson_from_flood_depth_no_flood():
    service = GISPostProcessorService()
    flood_depth = np.zeros(25) # 5x5 grid
    job_id = "test_job_id_geojson_no_flood"
    parameters = {"grid_resolution": 5, "flood_threshold": 0.1}
    feature_collection = service._generate_geojson_from_flood_depth(flood_depth, job_id, parameters)
    assert len(feature_collection["features"]) == 0

def test_generate_geojson_from_flood_depth_partial_flood():
    service = GISPostProcessorService()
    # 3x3 grid, flood at (0,0), (1,1), (2,2)
    flood_depth = np.array([
        0.2, 0.0, 0.0,
        0.0, 0.3, 0.0,
        0.0, 0.0, 0.4
    ])
    job_id = "test_job_id_geojson_partial_flood"
    parameters = {"grid_resolution": 3, "flood_threshold": 0.15}
    feature_collection = service._generate_geojson_from_flood_depth(flood_depth, job_id, parameters)
    assert len(feature_collection["features"]) == 3

    # Check properties of one feature
    feature = feature_collection["features"][0]
    assert feature["properties"]["job_id"] == job_id
    assert feature["properties"]["row"] == 0
    assert feature["properties"]["col"] == 0
    assert feature["properties"]["flood_depth"] == pytest.approx(0.2)
    assert feature["geometry"]["type"] == "Polygon"
    # Check coordinates for cell (0,0)
    expected_coords = [[(0,0), (1,0), (1,1), (0,1), (0,0)]]
    assert feature["geometry"]["coordinates"] == expected_coords

def test_generate_geojson_from_flood_depth_grid_mismatch_fallback_point(caplog):
    service = GISPostProcessorService()
    flood_depth = np.array([0.5, 0.6]) # 2 elements, but expecting 3x3=9
    job_id = "test_job_id_mismatch"
    parameters = {"grid_resolution": 3, "flood_threshold": 0.1}

    with caplog.at_level(20): # INFO level
        feature_collection = service._generate_geojson_from_flood_depth(flood_depth, job_id, parameters)

    assert len(feature_collection["features"]) == 1
    feature = feature_collection["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert feature["properties"]["average_flood_depth"] == pytest.approx(0.55)
    assert "Flood depth vector size (2) does not match expected grid_resolution (3x3)." in caplog.text

def test_generate_pdf_report_content():
    service = GISPostProcessorService()
    job_id = "test_job_id_pdf"
    parameters = {
        "solver_type": "CLASSICAL",
        "grid_resolution": 2,
        "flood_threshold": 0.1
    }
    geojson_path = "jobs/test_job_id_pdf/results/flood_data.geojson"
    solution_path = "jobs/test_job_id_pdf/solution_x.npy"
    flood_depth = np.array([
        0.0, 0.2,
        0.3, 0.0
    ]) # 2x2 grid, (0,1) and (1,0) are flooded

    report_bytes = service._generate_pdf_report(job_id, parameters, geojson_path, solution_path, flood_depth)
    report_content = report_bytes.decode('utf-8')

    assert f"Flood Simulation Report for Job ID: {job_id}" in report_content
    assert f"Solver Type: CLASSICAL" in report_content
    assert f"Grid Resolution: 2x2" in report_content
    assert f"Flood Threshold: 0.10" in report_content
    assert f"Max Flood Depth: {np.max(flood_depth):.2f}" in report_content
    assert f"Min Flood Depth: {np.min(flood_depth):.2f}" in report_content
    assert f"Average Flood Depth: {np.mean(flood_depth):.2f}" in report_content
    assert f"Flooded Cells: 2 / 4 (50.00%)" in report_content
    assert "--- Simulated Flood Map (F=Flooded, .=Dry) ---" in report_content
    assert " . F " in report_content # Row 0
    assert " F . " in report_content # Row 1

def test_postprocess_solution_uploads_files(mock_minio_client):
    service = GISPostProcessorService()
    job_id = "test_job_id_postprocess"
    solution_path = "jobs/test_job_id_postprocess/solution_x.npy"
    parameters = {
        "grid_resolution": 2,
        "conversion_factor": 0.5,
        "base_elevation": 0.0,
        "water_level_offset": 0.0,
        "flood_threshold": 0.1
    }

    # Mock solution download
    solution_vector = np.array([0.5, 0.8, 1.2, 0.1]) # 2x2 grid
    solution_bio = io.BytesIO()
    np.save(solution_bio, solution_vector)
    solution_bio.seek(0)
    mock_minio_client.download_file.return_value = solution_bio.getvalue()
    mock_minio_client.upload_file.return_value = None

    geojson_path, pdf_report_path = service.postprocess_solution(solution_path, job_id, parameters)

    assert geojson_path.startswith(f"jobs/{job_id}/results/flood_data_")
    assert pdf_report_path.startswith(f"jobs/{job_id}/results/flood_report_")

    # Verify download call
    mock_minio_client.download_file.assert_called_once_with(solution_path)

    # Verify upload calls (GeoJSON and PDF)
    assert mock_minio_client.upload_file.call_count == 2

    # Check GeoJSON upload
    geojson_call = mock_minio_client.upload_file.call_args_list[0]
    assert geojson_call.args[0] == geojson_path
    assert geojson_call.args[3] == "application/geo+json"
    uploaded_geojson = json.loads(geojson_call.args[1].decode('utf-8'))
    assert len(uploaded_geojson["features"]) > 0 # Should have flooded cells

    # Check PDF upload
    pdf_call = mock_minio_client.upload_file.call_args_list[1]
    assert pdf_call.args[0] == pdf_report_path
    assert pdf_call.args[3] == "application/pdf"
    uploaded_pdf_content = pdf_call.args[1].decode('utf-8')
    assert f"Flood Simulation Report for Job ID: {job_id}" in uploaded_pdf_content
