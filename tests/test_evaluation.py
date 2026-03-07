import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_s3_client():
    with patch("playground.routers.evaluation.get_s3_client") as mock:
        client = MagicMock()
        client.generate_signed_url.return_value = "https://example.com/result-url"
        mock.return_value = client
        yield client


@pytest.fixture
def mock_rate_limiter():
    with patch("playground.routers.evaluation.get_rate_limiter") as mock:
        limiter = MagicMock()
        limiter.acquire.return_value = True
        mock.return_value = limiter
        yield limiter


def test_evaluate_success(client, mock_s3_client, mock_rate_limiter):
    response = client.post(
        "/evaluate",
        json={
            "model_name": "test-model",
            "concurrent": 1,
            "signed_url": "https://example.com/file.csv",
        },
    )
    assert response.status_code == 200
    assert "result_url" in response.json()


def test_evaluate_invalid_concurrent(client, mock_rate_limiter):
    response = client.post(
        "/evaluate",
        json={
            "model_name": "test-model",
            "concurrent": 100,
            "signed_url": "https://example.com/file.csv",
        },
    )
    assert response.status_code == 400


def test_evaluate_rate_limit_exceeded(client, mock_rate_limiter):
    mock_rate_limiter.acquire.return_value = False
    response = client.post(
        "/evaluate",
        json={
            "model_name": "test-model",
            "concurrent": 1,
            "signed_url": "https://example.com/file.csv",
        },
    )
    assert response.status_code == 429
