import json
import logging
import traceback
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/chat/diag")
async def chat_diag():
    results = {}

    try:
        from models import ChatRequest
        results["import_models"] = "ok"
    except Exception as e:
        results["import_models"] = f"FAIL: {e}"

    try:
        from services.embeddings import embed
        results["import_embeddings"] = "ok"
    except Exception as e:
        results["import_embeddings"] = f"FAIL: {e}"

    try:
        from services.vector_store import search
        results["import_vector_store"] = "ok"
    except Exception as e:
        results["import_vector_store"] = f"FAIL: {e}"

    try:
        from services.llm import generate_response
        results["import_llm"] = "ok"
    except Exception as e:
        results["import_llm"] = f"FAIL: {e}"

    try:
        from services import conversations as conv_service
        results["import_conversations"] = "ok"
    except Exception as e:
        results["import_conversations"] = f"FAIL: {e}"

    try:
        from config import GROQ_API_KEY, QDRANT_URL, QDRANT_API_KEY
        results["config_loaded"] = "ok"
        results["groq_key_set"] = bool(GROQ_API_KEY)
        results["qdrant_url_set"] = bool(QDRANT_URL)
        results["qdrant_key_set"] = bool(QDRANT_API_KEY)
    except Exception as e:
        results["config_loaded"] = f"FAIL: {e}"

    try:
        from services.embeddings import _get_model
        results["embed_model_load"] = "skip"
    except Exception as e:
        results["embed_model_load"] = f"FAIL: {e}"

    try:
        from groq import AsyncGroq
        from config import GROQ_API_KEY
        client = AsyncGroq(api_key=GROQ_API_KEY)
        import httpx
        results["groq_client"] = "ok"
    except Exception as e:
        results["groq_client"] = f"FAIL: {e}"

    try:
        from qdrant_client import QdrantClient
        from config import QDRANT_URL, QDRANT_API_KEY
        qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        results["qdrant_client"] = "ok"
        results["qdrant_collections"] = qdrant.get_collections().collections
    except Exception as e:
        results["qdrant_client"] = f"FAIL: {e}"
        results["qdrant_error_detail"] = traceback.format_exc()

    return {"results": results}
