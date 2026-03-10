import redis
import hashlib
import json
import logging

class Cache:
    """Кеширование популярных запросов."""
    def __init__(self, host="localhost", port=6379, ttl=3600):
        try:
            self.r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
            self.r.ping() # проверка
            self.ttl = ttl
        except Exception as e:
            logging.warning(f"Redis cache not available: {e}")
            self.r = None

    def _hash(self, key: str) -> str:
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def get(self, question: str):
        if not self.r: return None
        data = self.r.get(self._hash(question))
        return json.loads(data) if data else None

    def set(self, question: str, response: dict):
        if self.r:
            self.r.set(self._hash(question), json.dumps(response), ex=self.ttl)
