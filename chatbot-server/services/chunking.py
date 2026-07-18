from typing import Optional

MAX_CHUNK_SIZE = 700
OVERLAP = 100


def chunk_document(
    text: str,
    source: Optional[str] = None,
    title: Optional[str] = None,
    page: Optional[int] = None,
    section: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> list[dict]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    buffer = ""
    chunk_index = 0

    for para in paragraphs:
        if not para:
            continue
        if len(buffer + " " + para) > MAX_CHUNK_SIZE and buffer:
            chunks.append(
                {
                    "text": buffer.strip(),
                    "metadata": {
                        "source": source or "",
                        "title": title or "",
                        "page": page,
                        "section": section or "",
                        "category": category or "general",
                        "tags": tags or [],
                        "chunkIndex": chunk_index,
                    },
                }
            )
            buffer = buffer[-OVERLAP:] + " " + para
            chunk_index += 1
        else:
            buffer = (buffer + "\n\n" + para) if buffer else para

    if buffer.strip():
        chunks.append(
            {
                "text": buffer.strip(),
                "metadata": {
                    "source": source or "",
                    "title": title or "",
                    "page": page,
                    "section": section or "",
                    "category": category or "general",
                    "tags": tags or [],
                    "chunkIndex": chunk_index,
                },
            }
        )

    return chunks
