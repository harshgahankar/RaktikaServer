from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import QDRANT_URL, QDRANT_API_KEY

COLLECTION = "raktika_knowledge_base"

try:
    from config import EMBEDDING_MODEL as _em
    if "large" in _em:
        VECTOR_SIZE = 1024
    elif "base" in _em:
        VECTOR_SIZE = 768
    else:
        VECTOR_SIZE = 384
except Exception:
    VECTOR_SIZE = 384

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None)
    return _client


async def ensure_collection():
    client = _get_client()
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION for c in collections)
    if not exists:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


async def upsert_points(points: list[dict]):
    await ensure_collection()
    client = _get_client()
    qdrant_points = [
        PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
        for p in points
    ]
    client.upsert(collection_name=COLLECTION, points=qdrant_points)


async def search(
    vector: list[float], top_k: int = 5, qdrant_filter: dict | None = None
) -> list[dict]:
    client = _get_client()
    try:
        results = client.search(
            collection_name=COLLECTION,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
        )
    except AttributeError:
        results = client.query_points(
            collection_name=COLLECTION, query=vector, limit=top_k, with_payload=True
        ).points
    return [
        {
            "text": r.payload.get("text", ""),
            "source": r.payload.get("source", ""),
            "title": r.payload.get("title", ""),
            "score": r.score,
        }
        for r in results
    ]
