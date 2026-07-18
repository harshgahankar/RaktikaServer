from fastapi import APIRouter, HTTPException
from models import IndexBatchRequest, SingleIndexRequest
from services.embeddings import embed
from services.vector_store import upsert_points
from services.chunking import chunk_document

router = APIRouter()


@router.post("/api/index/documents")
async def index_documents(req: IndexBatchRequest):
    if not req.documents:
        raise HTTPException(status_code=400, detail="documents array is required")

    points = []
    point_id = int(__import__("time").time() * 1000)

    for doc in req.documents:
        chunks = chunk_document(
            text=doc.text,
            source=doc.source,
            title=doc.title,
            page=doc.page,
            section=doc.section,
            category=doc.category,
            tags=doc.tags,
        )
        for chunk in chunks:
            vector = await embed(chunk["text"])
            points.append(
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": {**chunk["metadata"], "text": chunk["text"]},
                }
            )
            point_id += 1

    if points:
        await upsert_points(points)

    return {"success": True, "indexed": len(points)}


@router.post("/api/index/single")
async def index_single(req: SingleIndexRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="text is required")

    chunks = chunk_document(
        text=req.text,
        source=req.source,
        title=req.title,
        page=req.page,
        section=req.section,
        category=req.category,
        tags=req.tags,
    )

    points = []
    point_id = int(__import__("time").time() * 1000)

    for chunk in chunks:
        vector = await embed(chunk["text"])
        points.append(
            {
                "id": point_id,
                "vector": vector,
                "payload": {**chunk["metadata"], "text": chunk["text"]},
            }
        )
        point_id += 1

    if points:
        await upsert_points(points)

    return {"success": True, "indexed": len(points)}
