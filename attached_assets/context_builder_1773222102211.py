MAX_CHUNK_CHARS = 1500

class ContextBuilder:
    """Сборка контекста и сжатие информации из чанков."""
    def build(self, chunks: list[dict]) -> str:
        context_parts = []
        for chunk in chunks[:5]:
            title = chunk.get("title", "Unknown")
            section = chunk.get("section", title)
            source = f"{title}" if section == title else f"{title} - {section}"
            
            url = chunk.get("url")
            if url:
                source += f" (URL: {url})"
            
            text = chunk.get("text", "")
            if len(text) > MAX_CHUNK_CHARS:
                text = text[:MAX_CHUNK_CHARS] + "..."
            context_parts.append(f"--- DOCUMENT SECTION: {source} ---\n{text}")

        return "\n\n".join(context_parts)
