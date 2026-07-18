import logging
import hashlib

logger = logging.getLogger(__name__)

# NOTE: fastembed causes native crashes (segfault/OOM) on Render's free tier.
# Using a simple hash-based deterministic embedding as fallback.
# Replace with a real embedding service/API when needed.

DIMENSION = 384


async def embed(text: str) -> list[float]:
    h = hashlib.sha256(text.encode()).digest()
    vec = [((h[i % 32] + (i * 0.1)) % 1.0) for i in range(DIMENSION)]
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


async def embed_batch(texts: list[str]) -> list[list[float]]:
    return [await embed(t) for t in texts]
