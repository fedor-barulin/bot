from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import RAGPipeline
from cache import Cache
from analytics import Analytics
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Telecom AI Support API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация компонент
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
LLM_MODEL = os.getenv("LLM_MODEL", "")

pipeline = RAGPipeline(llm_model=LLM_MODEL, qdrant_host=QDRANT_HOST)
cache = Cache(host=REDIS_HOST)
analytics = Analytics()

@app.on_event("startup")
async def preload_models():
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, pipeline.hybrid_search._get_encoder)

# Модели API
class MessageItem(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    question: str
    history: list[MessageItem] = []

class SourceItem(BaseModel):
    title: str
    section: str
    page: int

class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Проверка кеша (кеш используем только если пустая история, иначе могут быть конфликты)
    cached = cache.get(request.question) if not request.history else None
    if cached:
        return cached

    # RAG Pipeline
    history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
    answer, chunks, p_time = pipeline.process(request.question, history=history_dicts)
    
    # Формирование ссылок на источники
    sources = []
    seen = set()
    for chunk in chunks:
        title = chunk.get("title", "Unknown")
        section = chunk.get("section", "Unknown")
        page = chunk.get("page", 0)
        source_key = f"{title}_{section}_{page}"
        
        if source_key not in seen:
            seen.add(source_key)
            sources.append(SourceItem(title=title, section=section, page=page))
    
    response_data = {"answer": answer, "sources": [s.model_dump() for s in sources]}
    
    # Сохранение в истории и кеширование
    cache.set(request.question, response_data)
    analytics.log_interaction(request.question, answer, chunks, p_time)
    
    return response_data
