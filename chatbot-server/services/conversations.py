import json
import os
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")


def _ensure_dir():
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)


def _file_path(conversation_id: str) -> str:
    return os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")


def create_conversation(user_id: str, role: str) -> dict:
    _ensure_dir()
    conv = {
        "id": str(uuid4()),
        "userId": user_id,
        "role": role,
        "title": "New conversation",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "messages": [],
    }
    with open(_file_path(conv["id"]), "w") as f:
        json.dump(conv, f, indent=2)
    return conv


def get_conversation(conversation_id: str) -> Optional[dict]:
    _ensure_dir()
    fp = _file_path(conversation_id)
    if not os.path.exists(fp):
        return None
    with open(fp) as f:
        return json.load(f)


def add_message(conversation_id: str, message: dict) -> Optional[dict]:
    conv = get_conversation(conversation_id)
    if not conv:
        return None
    msg = {
        "id": message.get("id", str(uuid4())),
        "role": message["role"],
        "content": message["content"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "liked": None,
        "sources": message.get("sources", []),
    }
    conv["messages"].append(msg)
    conv["updatedAt"] = datetime.now(timezone.utc).isoformat()
    if len(conv["messages"]) <= 2:
        user_msgs = [m for m in conv["messages"] if m["role"] == "user"]
        if user_msgs:
            conv["title"] = user_msgs[0]["content"][:80]
    with open(_file_path(conversation_id), "w") as f:
        json.dump(conv, f, indent=2)
    return conv


def list_conversations(user_id: str) -> list[dict]:
    _ensure_dir()
    conversations = []
    for fname in os.listdir(CONVERSATIONS_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(CONVERSATIONS_DIR, fname)) as f:
            conv = json.load(f)
        if conv.get("userId") == user_id:
            conversations.append(
                {
                    "id": conv["id"],
                    "title": conv["title"],
                    "role": conv.get("role", "patient"),
                    "createdAt": conv["createdAt"],
                    "updatedAt": conv["updatedAt"],
                    "messageCount": len(conv["messages"]),
                }
            )
    conversations.sort(key=lambda c: c["updatedAt"], reverse=True)
    return conversations


def search_messages(user_id: str, query: str) -> list[dict]:
    _ensure_dir()
    results = []
    query_lower = query.lower()
    for fname in os.listdir(CONVERSATIONS_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(CONVERSATIONS_DIR, fname)) as f:
            conv = json.load(f)
        if conv.get("userId") != user_id:
            continue
        for msg in conv["messages"]:
            if query_lower in msg["content"].lower():
                results.append(
                    {
                        **msg,
                        "conversationId": conv["id"],
                        "conversationTitle": conv["title"],
                    }
                )
    return results


def rate_message(conversation_id: str, message_id: str, liked: bool) -> Optional[dict]:
    conv = get_conversation(conversation_id)
    if not conv:
        return None
    for msg in conv["messages"]:
        if msg["id"] == message_id:
            msg["liked"] = liked
            with open(_file_path(conversation_id), "w") as f:
                json.dump(conv, f, indent=2)
            return conv
    return None


def delete_conversation(conversation_id: str) -> bool:
    fp = _file_path(conversation_id)
    if os.path.exists(fp):
        os.remove(fp)
        return True
    return False


def clear_conversation(conversation_id: str) -> Optional[dict]:
    conv = get_conversation(conversation_id)
    if not conv:
        return None
    conv["messages"] = []
    conv["updatedAt"] = datetime.now(timezone.utc).isoformat()
    with open(_file_path(conversation_id), "w") as f:
        json.dump(conv, f, indent=2)
    return conv


def get_history(conversation_id: str) -> list[dict]:
    conv = get_conversation(conversation_id)
    if not conv:
        return []
    return [
        {"role": m["role"], "content": m["content"]}
        for m in conv["messages"][-20:]
    ]
