import re

FILLERS = [
    "Конечно",
    "Вы можете",
    "Как правило",
    "Следует учитывать",
    "В большинстве случаев"
]

class ResponseCleaner:
    """Очистка ответа от мусора и ограничение длины."""
    
    def clean(self, text: str) -> str:
        if "Информация отсутствует в базе знаний" in text:
            return "Информация отсутствует в базе знаний"
            
        cleaned_text = text
        for filler in FILLERS:
            # Remove filler phrases, case-insensitive
            pattern = re.compile(rf"(?i)\b{filler}[,\s]*")
            cleaned_text = pattern.sub("", cleaned_text)
            
        # Ensure max 5 sentences
        # Splitting by common sentence endings
        lines = cleaned_text.split('\n')
        final_lines = []
        sentence_count = 0
        
        for line in lines:
            if line.strip().startswith("Источник:") or line.strip().startswith("URL:"):
                # Always preserve the source line regardless of sentence limit
                final_lines.append(line)
                continue
                
            # Count sentences in the line
            sentences_in_line = [s for s in re.split(r'(?<=[.!?])\s+', line) if s.strip()]
            
            if sentence_count + len(sentences_in_line) <= 5:
                final_lines.append(line)
                sentence_count += len(sentences_in_line)
            else:
                # Add only the remaining allowed sentences
                remaining = 5 - sentence_count
                if remaining > 0:
                    allowed_sentences = sentences_in_line[:remaining]
                    final_lines.append(" ".join(allowed_sentences))
                    sentence_count += remaining
                
                # Допускается продолжить цикл, чтобы не обрезать строку Источник, если она идет после лимита
                
        final_text = "\n".join(final_lines).strip()
        
        # Capitalize first letter just in case cleanup removed it
        if final_text and final_text[0].islower():
            final_text = final_text[0].upper() + final_text[1:]
            
        return final_text
