from fastapi import APIRouter, HTTPException, Query
from models import RateRequest
from services import conversations as conv_service

router = APIRouter()


@router.get("/api/conversations/{user_id}")
async def list_conversations(user_id: str):
    conversations = conv_service.list_conversations(user_id)
    return {"conversations": conversations}


@router.get("/api/conversations/detail/{conversation_id}")
async def get_conversation_detail(conversation_id: str):
    conv = conv_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation": conv}


@router.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    deleted = conv_service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}


@router.post("/api/conversations/{conversation_id}/clear")
async def clear_conversation(conversation_id: str):
    conv = conv_service.clear_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}


@router.get("/api/conversations/search/{user_id}")
async def search_messages(user_id: str, q: str = Query(...)):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter q is required")
    results = conv_service.search_messages(user_id, q)
    return {"results": results}


@router.post("/api/conversations/{conversation_id}/messages/{message_id}/rate")
async def rate_message(conversation_id: str, message_id: str, body: RateRequest):
    conv = conv_service.rate_message(conversation_id, message_id, body.liked)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation or message not found")
    return {"success": True}
