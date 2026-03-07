import asyncio
import hashlib
import logging
import time
from enum import Enum
from threading import Lock

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from tenacity import retry, stop_after_attempt, wait_exponential

from playground.config import get_settings

logger = logging.getLogger(__name__)


class ModelName(str, Enum):
    """Supported LLM model names."""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    OLLAMA_LLAMA3 = "llama3"
    OLLAMA_MISTRAL = "mistral"


def init_model(model_name: ModelName) -> ChatOpenAI | ChatAnthropic | ChatOllama:
    """Initialize a langchain LLM based on the model name."""
    settings = get_settings()

    if model_name in (ModelName.GPT_4O, ModelName.GPT_4O_MINI):
        return ChatOpenAI(
            model=model_name.value,
            api_key=settings.openai_api_key or "dummy",  # type: ignore[arg-type]
            temperature=0.7,
        )
    elif model_name in (ModelName.CLAUDE_3_5_SONNET, ModelName.CLAUDE_3_HAIKU):
        return ChatAnthropic(
            model_name=model_name.value,
            api_key=settings.anthropic_api_key or "dummy",  # type: ignore[arg-type]
            temperature=0.7,
            timeout=60,  # type: ignore[arg-type]
            stop=None,  # type: ignore[arg-type]
        )
    elif model_name in (ModelName.OLLAMA_LLAMA3, ModelName.OLLAMA_MISTRAL):
        return ChatOllama(
            model=model_name.value,
            temperature=0.7,
        )
    msg = f"Unsupported model: {model_name}"
    raise ValueError(msg)


retry_decorator = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)


@retry_decorator
def run_single_llm(
    model: ChatOpenAI | ChatAnthropic | ChatOllama,
    prompt: str,
) -> str:
    """Run a single LLM query with retry logic."""
    response = model.invoke(prompt)
    content = response.content
    if isinstance(content, str):
        return content
    return str(content)


@retry_decorator
def evaluate_single(
    model: ChatOpenAI | ChatAnthropic | ChatOllama,
    query: str,
    result: str,
    ground_truth: str,
    evaluation_prompt: str,
) -> dict:
    """Evaluate a single result with retry logic."""
    from playground.prompts import DEFAULT_CORRECTNESS_EVALUATION_PROMPT

    prompt = DEFAULT_CORRECTNESS_EVALUATION_PROMPT.format(
        query=query,
        result=result,
        ground_truth=ground_truth,
    )
    response = model.invoke(prompt)
    import json

    content: str = response.content  # type: ignore[assignment]
    if isinstance(content, list):
        content = content[0] if content else ""
    elif not isinstance(content, str):
        content = str(content)

    try:
        evaluation: dict = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        evaluation = {
            "correct": False,
            "score": 0.0,
            "feedback": f"Failed to parse evaluation response: {response.content}",
        }
    return evaluation


def compute_file_hash(content: bytes) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: int) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        tokens_to_add = int(elapsed * self.refill_rate)
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def acquire(self, tokens: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    async def acquire_async(self, tokens: int = 1) -> bool:
        while True:
            if self.acquire(tokens):
                return True
            await asyncio.sleep(0.1)


_rate_limiter: TokenBucketRateLimiter | None = None


def get_rate_limiter() -> TokenBucketRateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        settings = get_settings()
        _rate_limiter = TokenBucketRateLimiter(
            capacity=settings.token_bucket_capacity,
            refill_rate=settings.token_bucket_refill_rate,
        )
    return _rate_limiter
