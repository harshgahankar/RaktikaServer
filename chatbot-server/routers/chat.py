import json
import logging
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import ChatRequest
from services.embeddings import embed
from services.vector_store import search as vector_search
from services.llm import generate_response, stream_response
from services import conversations as conv_service

logger = logging.getLogger(__name__)
router = APIRouter()


async def _get_context_chunks(message: str):
    try:
        query_embedding = await embed(message)
        search_results = await vector_search(query_embedding, top_k=5)
        return [
            {"text": r["text"], "source": r["source"], "title": r["title"], "score": r["score"]}
            for r in search_results
        ]
    except Exception as e:
        logger.warning(f"Embedding/search failed, continuing without RAG: {e}")
        logger.warning(traceback.format_exc())
        return []


def _make_sources(context_chunks: list[dict]) -> list[dict]:
    return [
        {"title": c["title"], "source": c["source"]}
        for c in context_chunks
        if c.get("score", 0) > 0.7
    ]


@router.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.message or not req.userId:
        raise HTTPException(status_code=400, detail="message and userId are required")

    user_role = "doctor" if req.role == "doctor" else "patient"

    conv = conv_service.get_conversation(req.conversationId) if req.conversationId else None
    if not conv:
        conv = conv_service.create_conversation(req.userId, user_role)

    conv_service.add_message(conv["id"], {"role": "user", "content": req.message})

    context_chunks = await _get_context_chunks(req.message)
    history = conv_service.get_history(conv["id"])

    reply = await generate_response(
        messages=history,
        context_chunks=context_chunks,
        role=user_role,
    )

    updated_conv = conv_service.add_message(
        conv["id"], {"role": "assistant", "content": reply}
    )
    last_msg = updated_conv["messages"][-1]

    return {
        "reply": reply,
        "conversationId": conv["id"],
        "messageId": last_msg["id"],
        "sources": _make_sources(context_chunks),
    }


@router.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    if not req.message or not req.userId:
        raise HTTPException(status_code=400, detail="message and userId are required")

    user_role = "doctor" if req.role == "doctor" else "patient"

    conv = conv_service.get_conversation(req.conversationId) if req.conversationId else None
    if not conv:
        conv = conv_service.create_conversation(req.userId, user_role)

    conv_service.add_message(conv["id"], {"role": "user", "content": req.message})

    context_chunks = await _get_context_chunks(req.message)
    history = conv_service.get_history(conv["id"])

    async def event_stream():
        full_reply = ""
        try:
            async for token in stream_response(
                messages=history, context_chunks=context_chunks, role=user_role
            ):
                full_reply += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        bot_msg = {
            "role": "assistant",
            "content": full_reply,
            "sources": [c for c in context_chunks if c.get("score", 0) > 0.7],
        }
        updated_conv = conv_service.add_message(conv["id"], bot_msg)
        last_msg = updated_conv["messages"][-1]

        yield (
            f"data: {json.dumps({'done': True, 'messageId': last_msg['id'], 'sources': [{'title': s['title'], 'source': s['source']} for s in bot_msg['sources']]})}\n\n"
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-Id": conv["id"],
        },
    )
