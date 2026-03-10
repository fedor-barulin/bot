import logging
from datetime import datetime

logging.basicConfig(filename='analytics.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

class Analytics:
    """Логирование работы системы для аналитики."""
    def log_interaction(self, question: str, answer: str, chunks_used: list[dict], processing_time: float):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer_length": len(answer),
            "chunks_used": [c.get("chunk_id") for c in chunks_used],
            "processing_time_sec": round(processing_time, 3)
        }
        logging.info(str(log_entry))
