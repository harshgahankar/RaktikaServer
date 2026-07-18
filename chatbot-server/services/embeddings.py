import logging
import numpy as np

logger = logging.getLogger(__name__)

_model = None

try:
    from fastembed import TextEmbedding as _FastTextEmbedding
    _FASTEMBED_AVAILABLE = True
    logger.info("fastembed is available")
except ImportError as e:
    _FASTEMBED_AVAILABLE = False
    logger.warning(f"fastembed not available: {e}")


def _get_model():
    global _model
    if _model is None:
        if not _FASTEMBED_AVAILABLE:
            raise RuntimeError("fastembed is not installed")
        from config import EMBEDDING_MODEL
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = _FastTextEmbedding(model_name=EMBEDDING_MODEL)
        logger.info("Embedding model loaded")
    return _model


async def embed(text: str) -> list[float]:
    model = _get_model()
    result = list(model.embed([text]))[0]
    return result.tolist()


async def embed_batch(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return [r.tolist() for r in model.embed(texts)]
