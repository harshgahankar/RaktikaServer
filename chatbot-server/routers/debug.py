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
        from services.embeddings import embed, _get_model
        results["import_embeddings"] = "ok"
        try:
            m = _get_model()
            results["embed_model_loaded"] = "ok"
            emb = await embed("test")
            results["embed_dim"] = len(emb)
            results["embed_first_5"] = emb[:5]
        except Exception as e:
            results["embed_model_test"] = f"FAIL: {e}"
            results["embed_traceback"] = traceback.format_exc()
    except Exception as e:
        results["import_embeddings"] = f"FAIL: {e}"
        results["embed_traceback"] = traceback.format_exc()

    try:
        from services.vector_store import search
        results["import_vector_store"] = "ok"
        try:
            docs = await search([0.1] * 384, top_k=3)
            results["vector_search"] = "ok"
            results["vector_results"] = len(docs)
        except Exception as e:
            results["vector_search"] = f"FAIL: {e}"
    except Exception as e:
        results["import_vector_store"] = f"FAIL: {e}"

    try:
        from services.llm import generate_response
        results["import_llm"] = "ok"
        try:
            reply = await generate_response(
                messages=[{"role": "user", "content": "Say hello in one word."}],
                context_chunks=[],
                role="patient",
            )
            results["groq_response"] = reply[:100]
        except Exception as e:
            results["groq_response"] = f"FAIL: {e}"
            results["groq_traceback"] = traceback.format_exc()
    except Exception as e:
        results["import_llm"] = f"FAIL: {e}"

    try:
        from services import conversations as conv_service
        results["import_conversations"] = "ok"
        try:
            conv = conv_service.create_conversation("diag_user", "patient")
            results["conv_created"] = conv["id"]
            conv_service.add_message(conv["id"], {"role": "user", "content": "hello"})
            hist = conv_service.get_history(conv["id"])
            results["conv_history_len"] = len(hist)
        except Exception as e:
            results["conv_test"] = f"FAIL: {e}"
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

    return {"results": results}
