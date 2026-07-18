"""
Batch index all documents from the knowledge-base directory into Qdrant.
"""
import os
import sys
import json
import csv
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from services.embeddings import embed
from services.vector_store import upsert_points
from services.chunking import chunk_document


def run():
    kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge-base")
    os.makedirs(kb_dir, exist_ok=True)

    files = [
        f
        for f in os.listdir(kb_dir)
        if os.path.splitext(f)[1].lower() in (".md", ".txt", ".json", ".csv")
    ]
    print(f"Found {len(files)} files to index.")

    all_chunks = []

    for filename in files:
        filepath = os.path.join(kb_dir, filename)
        ext = os.path.splitext(filename)[1].lower()
        name = os.path.splitext(filename)[0]

        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        if ext == ".json":
            try:
                data = json.loads(content)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    text = item.get("text") or item.get("content") or json.dumps(item)
                    all_chunks.extend(
                        chunk_document(
                            text=text,
                            source=item.get("source", filename),
                            title=item.get("title", name),
                            category=item.get("category", "general"),
                            tags=item.get("tags", []),
                        )
                    )
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON file {filename}: {e}")
            continue

        if ext == ".csv":
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            if not lines:
                continue
            headers = [h.strip().lower() for h in lines[0].split(",")]
            for i in range(1, len(lines)):
                values = [v.strip() for v in lines[i].split(",")]
                row = {}
                for idx, h in enumerate(headers):
                    row[h] = values[idx] if idx < len(values) else ""
                text = " ".join(str(v) for v in row.values())
                all_chunks.extend(
                    chunk_document(
                        text=text,
                        source=filename,
                        title=row.get("title") or row.get("question") or f"{name} row {i}",
                        category=row.get("category", "general"),
                        tags=[t.strip() for t in row.get("tags", "").split(";") if t.strip()],
                    )
                )
            continue

        all_chunks.extend(
            chunk_document(
                text=content,
                source=filename,
                title=name,
                category="markdown" if ext == ".md" else "text",
                tags=[],
            )
        )

    if not all_chunks:
        print("No chunks generated.")
        return

    print(f"Generated {len(all_chunks)} chunks. Embedding...")

    point_id = int(time.time() * 1000)
    batch_size = 10

    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        points = []
        for chunk in batch:
            vector = embed(chunk["text"])
            points.append(
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": {**chunk["metadata"], "text": chunk["text"]},
                }
            )
            point_id += 1
        upsert_points(points)
        print(f"  Indexed batch {i // batch_size + 1} ({len(points)} chunks)")

    print(f"Done. Indexed {len(all_chunks)} chunks.")


if __name__ == "__main__":
    run()
