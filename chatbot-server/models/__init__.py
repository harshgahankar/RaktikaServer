from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None
    role: str = "patient"
    userId: str


class ChatResponse(BaseModel):
    reply: str
    conversationId: str
    messageId: Optional[str] = None
    sources: list[dict] = []


class RateRequest(BaseModel):
    liked: bool


class IndexDocument(BaseModel):
    text: str
    source: Optional[str] = None
    title: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = []


class IndexBatchRequest(BaseModel):
    documents: list[IndexDocument]


class SingleIndexRequest(IndexDocument):
    pass
