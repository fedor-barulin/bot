from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# 1. Подключение к Qdrant
client = QdrantClient(host="localhost", port=6333)
collection_name = "knowledge_base"

# 2. Создание коллекции под векторы размерности 1024 (bge-m3)
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
)

# 3. Инициализация энкодера
print("Loading model BAAI/bge-m3...")
encoder = SentenceTransformer("BAAI/bge-m3", device="cpu")

# 4. Пример чанка из базы знаний
chunk = {
    "chunk_id": 152,
    "title": "Мобильный интернет",
    "section": "Подключение",
    "text": "Подключение услуги выполняется USSD *104*18#. Для настройки APN используйте...",
    "tags": ["internet", "activation"],
    "source": "mobile_internet.pdf",
    "page": 3
}

# 5. Векторизация
vector = encoder.encode(chunk["text"]).tolist()

# 6. Загрузка в БД
client.upsert(
    collection_name=collection_name,
    points=[
        models.PointStruct(
            id=chunk["chunk_id"],
            payload=chunk,
            vector=vector
        )
    ]
)

print(f"Uploaded chunk '{chunk['title']}' successfully to Qdrant!")
