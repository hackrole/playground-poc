import logging
import uuid

from typing import TypedDict

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from playground.clients.s3_client import s3_client
from playground.constants import MAX_CONCURRENT, S3_RESULT_FOLDER
from playground.tasks import run_evaluation
from playground.utils import ModelName

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


class EvaluateRequest(BaseModel):
    model_name: ModelName
    concurrent: int = Field(default=1, ge=1, le=MAX_CONCURRENT)
    signed_url: str


class EvaluateResult(TypedDict):
    result_url: str


@router.post("")
async def evaluate(
    payload: EvaluateRequest,
    background_tasks: BackgroundTasks,
) -> EvaluateResult:
    """Trigger an LLM evaluation job.

    Args:
        request: Evaluation request containing model_name, concurrent, and signed_url.
        background_tasks: FastAPI background tasks for async processing.

    Returns:
        Dictionary containing result_url to access the evaluation results.

    Raises:
        HTTPException: If rate limit exceeded or evaluation fails.
    """
    model_name = payload.model_name
    concurrent = payload.concurrent
    signed_url = payload.signed_url

    job_id = str(uuid.uuid4())
    result_key = f"{S3_RESULT_FOLDER}/{job_id}.csv"

    background_tasks.add_task(
        run_evaluation, model_name.value, signed_url, concurrent, result_key, job_id
    )

    result_url = s3_client.generate_signed_url(result_key)

    return {"result_url": result_url}
