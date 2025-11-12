import pytest
from unittest.mock import MagicMock
from app.core.object_storage import MinioClient

@pytest.fixture
def mock_minio_client(mocker):
    """Fixture to mock MinioClient for isolated testing."""
    mock_client = MagicMock(spec=MinioClient)
    mocker.patch('app.core.object_storage.MinioClient', return_value=mock_client)
    return mock_client
