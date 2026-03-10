"""
Upload markdown-format RAG chunks to the Qdrant knowledge base.

Supports two modes:
  - Local disk mode (default): Qdrant data stored on disk, no server needed.
  - Server mode: Connect to a running Qdrant HTTP server.

Usage:
  # Local disk mode (default)
  python data/upload_markdown.py data/my_file.md

  # Server mode (Docker or remote Qdrant)
  python data/upload_markdown.py data/my_file.md --qdrant-host localhost
  python data/upload_markdown.py data/my_file.md --qdrant-host localhost --qdrant-port 6333

  # Or via environment variable
  QDRANT_HOST=localhost python data/upload_markdown.py data/my_file.md

Expected markdown format per chunk:
  ### [filename.pdf] Раздел: Section Name (Стр. page_num)
  **Теги:** tag1, tag2

  content text...

  ---
"""
import re
import os
import sys
import argparse

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

DEFAULT_LOCAL_STORAGE = os.path.join(os.path.dirname(__file__), "qdrant_storage")
COLLECTION_NAME = "knowledge_base"
VECTOR_SIZE = 1024
MODEL_NAME = "BAAI/bge-m3"

HEADER_RE = re.compile(
    r"###\s+\[(.+?)\]\s+Раздел:\s+(.+?)\s+\(Стр\.\s*(\d+)\)"
)
TAGS_RE = re.compile(r"\*\*Теги:\*\*\s*(.+)")


def parse_chunks(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    raw_blocks = re.split(r"\n---\n", content)
    chunks = []
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        header_match = HEADER_RE.search(block)
        if not header_match:
            continue

        filename = header_match.group(1).strip()
        section = header_match.group(2).strip()
        page = int(header_match.group(3))
        title = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)

        tags_match = TAGS_RE.search(block)
        if tags_match:
            raw_tags = tags_match.group(1).strip()
            tags = [] if raw_tags.lower() == "нет" else [t.strip() for t in raw_tags.split(",")]
        else:
            tags = []

        after_header = block[header_match.end():]
        if tags_match:
            tag_line_end = after_header.find("\n", after_header.find("**Теги:**"))
            text_start = tag_line_end + 1 if tag_line_end != -1 else 0
            text = after_header[text_start:].strip()
        else:
            text = after_header.strip()

        text = text.lstrip(", ").strip()

        if text:
            chunks.append({
                "title": title,
                "section": section,
                "page": page,
                "tags": tags,
                "text": text,
                "source": filename,
            })

    return chunks


def get_client(qdrant_host: str | None, qdrant_port: int) -> QdrantClient:
    host = qdrant_host or os.getenv("QDRANT_HOST")
    if host:
        print(f"Connecting to Qdrant server at {host}:{qdrant_port}")
        return QdrantClient(host=host, port=qdrant_port)
    else:
        print(f"Using local Qdrant disk storage at: {DEFAULT_LOCAL_STORAGE}")
        return QdrantClient(path=DEFAULT_LOCAL_STORAGE)


def ensure_collection(client: QdrantClient):
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        print(f"Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


def main():
    parser = argparse.ArgumentParser(description="Upload markdown RAG chunks to Qdrant knowledge base")
    parser.add_argument("filepath", help="Path to the markdown file with RAG chunks")
    parser.add_argument(
        "--qdrant-host",
        default=None,
        help="Qdrant server host (e.g. localhost). If not set, uses local disk storage."
    )
    parser.add_argument(
        "--qdrant-port",
        type=int,
        default=6333,
        help="Qdrant server port (default: 6333)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print(f"File not found: {args.filepath}")
        sys.exit(1)

    print(f"Parsing chunks from: {args.filepath}")
    chunks = parse_chunks(args.filepath)
    if not chunks:
        print("No chunks found. Make sure the file follows the expected format.")
        sys.exit(1)
    print(f"Found {len(chunks)} chunks")

    client = get_client(args.qdrant_host, args.qdrant_port)
    ensure_collection(client)

    start_id = client.count(collection_name=COLLECTION_NAME).count

    print(f"Loading embedding model '{MODEL_NAME}'... (first run downloads ~2.2 GB)")
    encoder = SentenceTransformer(MODEL_NAME, device="cpu")

    print("Vectorizing and uploading chunks...")
    points = []
    for i, chunk in enumerate(chunks):
        chunk_id = start_id + i
        vector = encoder.encode(chunk["text"]).tolist()
        payload = {
            "chunk_id": chunk_id,
            "title": chunk["title"],
            "section": chunk["section"],
            "page": chunk["page"],
            "tags": chunk["tags"],
            "text": chunk["text"],
            "source": chunk["source"],
        }
        points.append(models.PointStruct(id=chunk_id, payload=payload, vector=vector))
        print(f"  [{i+1}/{len(chunks)}] [{chunk['title']}] {chunk['section']} (Стр. {chunk['page']})")

    client.upsert(collection_name=COLLECTION_NAME, points=points)

    final_count = client.count(collection_name=COLLECTION_NAME).count
    print(f"\nДобавлено {len(points)} чанков. Всего в базе знаний: {final_count}")


if __name__ == "__main__":
    main()
