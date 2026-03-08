import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_s3_client():
    with patch("playground.routers.evaluation.s3_client") as mock:
        mock.generate_signed_url.return_value = "https://example.com/signed-url"
        yield mock


@pytest.fixture
def mock_rate_limiter():
    with patch("playground.routers.evaluation.get_rate_limiter") as mock:
        limiter = MagicMock()
        limiter.acquire.return_value = True
        mock.return_value = limiter
        yield limiter


@pytest.fixture
def mock_download_csv():
    with patch("playground.routers.evaluation._download_csv_from_signed_url") as mock:
        mock.return_value = [
            {"id": "1", "query": "What is 2+2?", "ground_truth": "4"},
            {
                "id": "2",
                "query": "What is the capital of France?",
                "ground_truth": "Paris",
            },
        ]
        yield mock


@pytest.fixture
def mock_batch_evaluate():
    with patch("playground.routers.evaluation.batch_evaluate") as mock:
        from playground.service.evaluation import EvaluationResult

        mock.return_value = [
            EvaluationResult(
                query="What is 2+2?",
                result="4",
                ground_truth="4",
                correct=True,
                score=1.0,
                feedback="Correct",
            ),
            EvaluationResult(
                query="What is the capital of France?",
                result="Paris",
                ground_truth="Paris",
                correct=True,
                score=1.0,
                feedback="Correct",
            ),
        ]
        yield mock


def test_evaluate_success(
    client, mock_s3_client, mock_rate_limiter, mock_download_csv, mock_batch_evaluate
):
    response = client.post(
        "/evaluate",
        json={
            "model_name": "gpt-4o",
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
            "model_name": "gpt-4o",
            "concurrent": 100,
            "signed_url": "https://example.com/file.csv",
        },
    )
    assert response.status_code == 422


def test_evaluate_rate_limit_exceeded(client, mock_rate_limiter):
    mock_rate_limiter.acquire.return_value = False
    response = client.post(
        "/evaluate",
        json={
            "model_name": "gpt-4o",
            "concurrent": 1,
            "signed_url": "https://example.com/file.csv",
        },
    )
    assert response.status_code == 429
