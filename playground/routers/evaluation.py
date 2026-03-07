import asyncio
import csv
import io
import logging
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from playground.clients.s3_client import StorageError, get_s3_client
from playground.constants import MAX_CONCURRENT, S3_RESULT_FOLDER
from playground.utils import get_rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


class EvaluateRequest(BaseModel):
    model_name: str
    concurrent: int = 1
    signed_url: str = ""


async def _run_evaluation(
    model_name: str,
    signed_url: str,
    result_key: str,
) -> None:
    """Run mock LLM evaluation.

    This is a placeholder for actual LLM evaluation logic.
    """
    await asyncio.sleep(1)

    results = [
        {"prompt": "What is 2+2?", "expected": "4", "actual": "4", "correct": True},
        {
            "prompt": "What is the capital of France?",
            "expected": "Paris",
            "actual": "Paris",
            "correct": True,
        },
        {"prompt": "What is 5*5?", "expected": "25", "actual": "25", "correct": True},
    ]

    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=["prompt", "expected", "actual", "correct"]
    )
    writer.writeheader()
    writer.writerows(results)

    get_s3_client().upload_csv(output.getvalue().encode(), result_key)


@router.post("")
async def evaluate(request: EvaluateRequest) -> dict[str, str]:
    """Trigger an LLM evaluation job.

    Args:
        request: Evaluation request containing model_name, concurrent, and signed_url.

    Returns:
        Dictionary containing result_url to access the evaluation results.

    Raises:
        HTTPException: If rate limit exceeded or evaluation fails.
    """
    model_name = request.model_name
    concurrent = request.concurrent
    signed_url = request.signed_url

    if concurrent < 1 or concurrent > MAX_CONCURRENT:
        raise HTTPException(
            status_code=400,
            detail=f"Concurrent must be between 1 and {MAX_CONCURRENT}",
        )

    rate_limiter = get_rate_limiter()
    if not rate_limiter.acquire(concurrent):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    result_key = f"{S3_RESULT_FOLDER}/{uuid.uuid4()}.csv"

    try:
        await _run_evaluation(model_name, signed_url, result_key)
    except StorageError as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Evaluation failed")

    try:
        result_url = get_s3_client().generate_signed_url(result_key)
    except StorageError as e:
        logger.error(f"Failed to generate result URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate result URL")

    return {"result_url": result_url}
