import csv
import io
import logging

import httpx

from playground.clients.s3_client import s3_client
from playground.constants import MAX_CONCURRENT
from playground.service.evaluation import EvaluationItem, batch_evaluate
from playground.utils import ModelName

logger = logging.getLogger(__name__)


async def run_evaluation(
    model_name: str,
    signed_url: str,
    concurrent: int,
    result_key: str,
    job_id: str,
) -> None:
    """Run LLM evaluation in background.

    Args:
        model_name: The model to use for evaluation.
        signed_url: The signed URL to download the input CSV.
        result_key: The S3 key to upload the results.
        job_id: The unique job identifier for logging.
    """
    try:
        rows = await _download_csv_from_signed_url(signed_url)

        items = [
            EvaluationItem(query=row["query"], ground_truth=row["ground_truth"])
            for row in rows
        ]

        try:
            model_enum = ModelName(model_name)
        except ValueError:
            logger.error(f"Invalid model name: {model_name}")
            return

        results = await batch_evaluate(
            model_name=model_enum,
            items=items,
            max_concurrency=concurrent,
        )

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "query",
                "ground_truth",
                "result",
                "correct",
                "score",
                "feedback",
            ],
        )
        writer.writeheader()

        for row, result in zip(rows, results):
            writer.writerow(
                {
                    "id": row["id"],
                    "query": row["query"],
                    "ground_truth": row["ground_truth"],
                    "result": result.result,
                    "correct": result.correct,
                    "score": result.score,
                    "feedback": result.feedback,
                }
            )

        s3_client.upload_csv(output.getvalue().encode(), result_key)
        logger.info(f"Evaluation job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Evaluation job {job_id} failed: {e}", exc_info=True)
        raise


async def _download_csv_from_signed_url(signed_url: str) -> list[dict[str, str]]:
    """Download and parse CSV from a signed URL.

    Args:
        signed_url: The signed URL to download the CSV from.

    Returns:
        List of dictionaries containing id, query, and ground_truth.

    Raises:
        HTTPException: If the download fails or CSV is invalid.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(signed_url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to download CSV: {e}")

    content = response.text
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    required_fields = {"id", "query", "ground_truth"}
    if not required_fields.issubset(rows[0].keys()):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {', '.join(required_fields)}",
        )

    return rows


class HTTPException(Exception):
    """HTTP Exception for task errors."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)
