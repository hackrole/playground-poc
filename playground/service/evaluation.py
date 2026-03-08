import asyncio
import logging
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

from playground.prompts import DEFAULT_RUN_PROMPT
from playground.utils import (
    ModelName,
    evaluate_single,
    get_rate_limiter,
    init_model,
    run_single_llm,
)

logger = logging.getLogger(__name__)


@dataclass
class EvaluationItem:
    """Single evaluation item."""

    query: str
    ground_truth: str


@dataclass
class EvaluationResult:
    """Result of a single evaluation."""

    query: str
    result: str
    ground_truth: str
    correct: bool
    score: float
    feedback: str


async def _run_single_item(
    model: ChatOpenAI | ChatAnthropic | ChatOllama,
    item: EvaluationItem,
    rate_limiter: asyncio.Semaphore,
) -> EvaluationResult:
    """Run a single evaluation item with rate limiting."""
    async with rate_limiter:
        while True:
            limiter = get_rate_limiter()
            if await limiter.acquire_async(tokens=1):
                break
            await asyncio.sleep(0.1)

        prompt = DEFAULT_RUN_PROMPT.format(query=item.query)
        result = run_single_llm(model, prompt)

        evaluation = evaluate_single(
            model=model,
            query=item.query,
            result=result,
            ground_truth=item.ground_truth,
            evaluation_prompt="",
        )

        return EvaluationResult(
            query=item.query,
            result=result,
            ground_truth=item.ground_truth,
            correct=evaluation.get("correct", False),
            score=evaluation.get("score", 0.0),
            feedback=evaluation.get("feedback", ""),
        )


async def batch_evaluate(
    model_name: ModelName,
    items: list[EvaluationItem],
    max_concurrency: int,
) -> list[EvaluationResult]:
    """Run batch evaluation with concurrency and rate limiting.

    Args:
        model_name: The model to use for evaluation.
        items: List of evaluation items.
        max_concurrency: Maximum number of concurrent requests.

    Returns:
        List of evaluation results.
    """
    model = init_model(model_name)
    rate_limiter = asyncio.Semaphore(max_concurrency)

    tasks = [_run_single_item(model, item, rate_limiter) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    evaluation_results: list[EvaluationResult] = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Evaluation failed: {result}")
            evaluation_results.append(
                EvaluationResult(
                    query="",
                    result="",
                    ground_truth="",
                    correct=False,
                    score=0.0,
                    feedback=f"Error: {str(result)}",
                )
            )
        elif isinstance(result, EvaluationResult):
            evaluation_results.append(result)
        else:
            evaluation_results.append(
                EvaluationResult(
                    query="",
                    result="",
                    ground_truth="",
                    correct=False,
                    score=0.0,
                    feedback="Unknown error",
                )
            )

    return evaluation_results
