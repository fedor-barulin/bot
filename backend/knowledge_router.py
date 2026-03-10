class KnowledgeRouter:
    """Маршрутизация запроса по разделам базы знаний на основе анализа."""
    
    def route(self, query_analysis: dict) -> list[str]:
        service = query_analysis.get("service", "").lower()
        
        # Эвристика по разделам
        sections = []
        if "internet" in service or "интернет" in service or "lte" in service:
            sections.append("Мобильный интернет")
        if "sms" in service or "смс" in service:
            sections.append("SMS")
        if "voice" in service or "голос" in service or "звонк" in service:
            sections.append("Голосовая связь")
            
        return sections
