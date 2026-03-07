import asyncio
import hashlib
import logging
import time
from threading import Lock

from playground.config import get_settings

logger = logging.getLogger(__name__)


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
