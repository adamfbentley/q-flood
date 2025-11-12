import pytest
import numpy as np
import json
import io
from unittest.mock import MagicMock
from app.services.geospatial_processor import GeospatialProcessorService
import rasterio
import fiona
from jsonschema import ValidationError

# Mock rasterio.open to avoid actual file system/GDAL dependencies
@pytest.fixture
def mock_rasterio_open(mocker):
    mock_src = MagicMock()
    mock_src.crs = 'EPSG:4326'
    mock_src.count = 1
    mock_src.width = 100
    mock_src.height = 50
    mock_src.res = (1.0, 1.0)
    mock_src.bounds = rasterio.coords.BoundingBox(left=0, bottom=0, right=100, top=50)
    mock_src.nodata = -9999
    mock_src.read.return_value = np.array([[10, 20], [30, 40]], dtype=np.float32)
    mocker.patch('rasterio.open', return_value=mock_src)
    return mock_src

# Mock fiona.open for shapefile validation
@pytest.fixture
def mock_fiona_open(mocker):
    mock_src = MagicMock()
    mock_src.__enter__.return_value = mock_src # Allow 'with' statement
    mock_src.__exit__.return_value = None
    mock_src.driver = 'ESRI Shapefile'
    mock_src.crs = {'init': 'epsg:4326'}
    mock_src.__len__.return_value = 1 # Simulate one feature
    mocker.patch('fiona.open', return_value=mock_src)
    return mock_src

@pytest.fixture
def geospatial_service():
    return GeospatialProcessorService()

class TestGeospatialProcessorService:
    job_id = "test-job-id"

    def test_validate_geotiff_successfully(self, geospatial_service, mock_rasterio_open):
        file_content = b'dummy_geotiff_content'
        file_type = 'image/tiff'
        assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is True
        mock_rasterio_open.assert_called_once()

    def test_validate_geotiff_no_bands_fails(self, geospatial_service, mock_rasterio_open, caplog):
        mock_rasterio_open.return_value.count = 0
        file_content = b'dummy_geotiff_content'
        file_type = 'image/tiff'
        with caplog.at_level('ERROR'):
            assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is False
        assert "GeoTIFF validation failed: No raster bands found." in caplog.text

    def test_validate_shapefile_successfully(self, geospatial_service, mock_fiona_open):
        file_content = b'dummy_shapefile_zip_content'
        file_type = 'application/zip'
        assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is True
        mock_fiona_open.assert_called_once()

    def test_validate_shapefile_no_features_warns(self, geospatial_service, mock_fiona_open, caplog):
        mock_fiona_open.return_value.__len__.return_value = 0
        file_content = b'dummy_shapefile_zip_content'
        file_type = 'application/zip'
        with caplog.at_level('WARNING'):
            assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is True # Still valid, just empty
        assert "Shapefile validation warning: No features found." in caplog.text

    def test_validate_json_config_successfully(self, geospatial_service):
        file_content = b'{"grid_resolution": 10, "custom_param": "value"}'
        file_type = 'application/json'
        assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is True

    def test_validate_json_config_invalid_schema_fails(self, geospatial_service, caplog):
        file_content = b'{"grid_resolution": "not_an_int"}'
        file_type = 'application/json'
        with caplog.at_level('ERROR'):
            assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is False
        assert "JSON config file validation failed: Schema mismatch" in caplog.text

    def test_validate_json_config_malformed_json_fails(self, geospatial_service, caplog):
        file_content = b'{invalid json}'
        file_type = 'application/json'
        with caplog.at_level('ERROR'):
            assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is False
        assert "JSON config file validation failed: Invalid JSON format" in caplog.text

    def test_validate_plain_text_successfully(self, geospatial_service):
        file_content = b'25'
        file_type = 'text/plain'
        assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is True

    def test_validate_plain_text_non_integer_fails(self, geospatial_service, caplog):
        file_content = b'not_an_integer'
        file_type = 'text/plain'
        with caplog.at_level('ERROR'):
            assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is False
        assert "Plain text file validation failed: Content is not a positive integer." in caplog.text

    def test_validate_unsupported_file_type_fails(self, geospatial_service, caplog):
        file_content = b'dummy_unsupported_content'
        file_type = 'application/octet-stream'
        with caplog.at_level('WARNING'):
            assert geospatial_service.validate_geospatial_data(file_content, file_type, self.job_id) is False
        assert "Validation failed: Unsupported file type 'application/octet-stream'." in caplog.text

    def test_preprocess_geotiff_extracts_metadata(self, geospatial_service, mock_rasterio_open):
        file_content = b'dummy_geotiff_content'
        file_type = 'image/tiff'
        parameters = {}

        preprocessed_content, content_type = geospatial_service.preprocess_geospatial_data(file_content, file_type, self.job_id, parameters)
        metadata = json.loads(preprocessed_content.decode('utf-8'))

        assert content_type == 'application/json'
        assert metadata['job_id'] == self.job_id
        assert metadata['original_file_type'] == file_type
        assert 'bounds' in metadata['extracted_parameters']
        assert metadata['extracted_parameters']['width'] == 100
        assert metadata['extracted_parameters']['height'] == 50
        assert metadata['extracted_parameters']['crs'] == 'EPSG:4326'
        assert metadata['extracted_parameters']['mean_value_band1'] == pytest.approx(25)
        assert metadata['extracted_parameters']['grid_resolution'] == 10 # min(100,50)//5

    def test_preprocess_json_config_merges_parameters(self, geospatial_service):
        file_content = b'{"grid_resolution": 25, "custom_param": "test"}'
        file_type = 'application/json'
        parameters = {"solver_option": "fast"}

        preprocessed_content, content_type = geospatial_service.preprocess_geospatial_data(file_content, file_type, self.job_id, parameters)
        metadata = json.loads(preprocessed_content.decode('utf-8'))

        assert content_type == 'application/json'
        assert metadata['extracted_parameters']['grid_resolution'] == 25
        assert metadata['extracted_parameters']['custom_param'] == 'test'
        assert metadata['extracted_parameters']['solver_option'] == 'fast'

    def test_preprocess_plain_text_config_for_grid_resolution(self, geospatial_service):
        file_content = b'30'
        file_type = 'text/plain'
        parameters = {}

        preprocessed_content, content_type = geospatial_service.preprocess_geospatial_data(file_content, file_type, self.job_id, parameters)
        metadata = json.loads(preprocessed_content.decode('utf-8'))

        assert content_type == 'application/json'
        assert metadata['extracted_parameters']['grid_resolution'] == 30

    def test_preprocess_shapefile_extracts_metadata(self, geospatial_service, mock_fiona_open):
        file_content = b'dummy_shapefile_zip_content'
        file_type = 'application/zip'
        parameters = {}

        preprocessed_content, content_type = geospatial_service.preprocess_geospatial_data(file_content, file_type, self.job_id, parameters)
        metadata = json.loads(preprocessed_content.decode('utf-8'))

        assert content_type == 'application/json'
        assert metadata['original_file_type'] == file_type
        assert 'bounds' in metadata['extracted_parameters']
        assert 'feature_count' in metadata['extracted_parameters']
        assert 'crs' in metadata['extracted_parameters']
        mock_fiona_open.assert_called_once()

    def test_preprocess_unknown_file_types_gracefully(self, geospatial_service, caplog):
        file_content = b'some_binary_data'
        file_type = 'application/octet-stream'
        parameters = {"default_grid": 10}

        with caplog.at_level('WARNING'):
            preprocessed_content, content_type = geospatial_service.preprocess_geospatial_data(file_content, file_type, self.job_id, parameters)
        metadata = json.loads(preprocessed_content.decode('utf-8'))

        assert content_type == 'application/json'
        assert metadata['extracted_parameters']['default_grid'] == 10
        assert metadata['original_file_type'] == file_type
        assert "No specific pre-processing implemented for file type 'application/octet-stream'." in caplog.text
