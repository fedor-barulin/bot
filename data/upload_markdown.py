"""
Upload markdown-format RAG chunks to the local Qdrant knowledge base.

Markdown format expected:
    ### [filename.pdf] Раздел: Section Name (Стр. page_num)
    **Теги:** tag1, tag2
    
    content text...
    
    ---
"""
import re
import os
import sys

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "qdrant_storage")
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_markdown.py <path_to_markdown_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    print(f"Parsing chunks from: {filepath}")
    chunks = parse_chunks(filepath)
    print(f"Found {len(chunks)} chunks")

    print(f"Connecting to local Qdrant storage at: {STORAGE_PATH}")
    client = QdrantClient(path=STORAGE_PATH)

    existing_collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing_collections:
        print(f"Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

    count_result = client.count(collection_name=COLLECTION_NAME)
    start_id = count_result.count

    print(f"Loading embedding model '{MODEL_NAME}'... (this may take a few minutes on first run)")
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
        print(f"  [{i+1}/{len(chunks)}] Encoded: [{chunk['title']}] {chunk['section']} (Стр. {chunk['page']})")

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"\nSuccessfully uploaded {len(points)} chunks to '{COLLECTION_NAME}'!")
    final_count = client.count(collection_name=COLLECTION_NAME).count
    print(f"Total chunks in knowledge base: {final_count}")


if __name__ == "__main__":
    main()
