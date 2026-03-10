class ContextBuilder:
    """Сборка контекста и сжатие информации из чанков."""
    def build(self, chunks: list[dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks):
            source_info = f"Источник: '{chunk.get('title', 'Unknown')}', Раздел: '{chunk.get('section', 'Unknown')}', Страница: {chunk.get('page', 0)}"
            text = chunk.get("text", "")
            context_parts.append(f"[{source_info}]\n{text}")
        
        return "\n\n".join(context_parts)
