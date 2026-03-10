MAX_CHUNK_CHARS = 1500

class ContextBuilder:
    """Сборка контекста и сжатие информации из чанков."""
    def build(self, chunks: list[dict]) -> str:
        context_parts = []
        for chunk in chunks:
            source_info = (
                f"Источник: '{chunk.get('title', 'Unknown')}', "
                f"Раздел: '{chunk.get('section', 'Unknown')}', "
                f"Страница: {chunk.get('page', 0)}"
            )
            text = chunk.get("text", "")
            if len(text) > MAX_CHUNK_CHARS:
                text = text[:MAX_CHUNK_CHARS] + "..."
            context_parts.append(f"[{source_info}]\n{text}")

        return "\n\n".join(context_parts)
