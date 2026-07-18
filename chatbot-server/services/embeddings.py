from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


async def embed(text: str) -> list[float]:
    model = _get_model()
    result = model.encode(text, normalize_embeddings=True)
    return result.tolist()


async def embed_batch(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    results = model.encode(texts, normalize_embeddings=True)
    return [r.tolist() for r in results]
