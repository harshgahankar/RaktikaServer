import numpy as np
from fastembed import TextEmbedding
from config import EMBEDDING_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


async def embed(text: str) -> list[float]:
    model = _get_model()
    result = list(model.embed([text]))[0]
    return result.tolist()


async def embed_batch(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return [r.tolist() for r in model.embed(texts)]
