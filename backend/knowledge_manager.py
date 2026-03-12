import re
import json

HEADER_RE = re.compile(
    r"###\s+\[(.+?)\]\s+Раздел:\s+(.+?)\s+\(Стр\.\s*(\d+)\)"
)
TAGS_RE = re.compile(r"\*\*Теги:\*\*\s*(.+)")


def parse_markdown(content: str) -> list[dict]:
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


def parse_json(content: str) -> list[dict]:
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("JSON must be a top-level array of chunk objects.")

    chunks = []
    for item in data:
        text = item.get("text", "").strip()
        if not text:
            continue
        title = item.get("title", "")
        source = item.get("source", f"{title}.pdf" if title else "unknown.pdf")
        chunks.append({
            "title": title,
            "section": item.get("section", ""),
            "page": int(item.get("page", 0)),
            "tags": item.get("tags") or [],
            "text": text,
            "source": source,
            "article_url": item.get("article_url", ""),
        })

    return chunks


def parse_file(filename: str, content: str) -> list[dict]:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "json":
        return parse_json(content)
    return parse_markdown(content)
