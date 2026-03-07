import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_s3_client():
    with patch("playground.routers.upload.get_s3_client") as mock:
        client = MagicMock()
        client.compute_file_hash.return_value = "abc123"
        client.upload_csv.return_value = None
        client.generate_signed_url.return_value = "https://example.com/signed-url"
        mock.return_value = client
        yield client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_upload_file_success(client, mock_s3_client):
    response = client.post(
        "/upload", files={"file": ("test.csv", "col1,col2\n1,2\n", "text/csv")}
    )
    assert response.status_code == 200
    assert "signed_url" in response.json()
    mock_s3_client.upload_csv.assert_called_once()


def test_upload_file_invalid(client):
    response = client.post("/upload")
    assert response.status_code == 422
