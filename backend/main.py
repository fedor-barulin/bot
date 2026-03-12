from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from rag_pipeline import RAGPipeline
from cache import Cache
from analytics import Analytics
from knowledge_manager import parse_file
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def preload_models():
    loop = asyncio.get_event_loop()
    encoder = await loop.run_in_executor(None, pipeline.hybrid_search._get_encoder)
    await loop.run_in_executor(None, encoder.encode, ["warmup"])

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
    url: str = ""

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
            sources.append(SourceItem(
                title=title,
                section=section,
                page=page,
                url=chunk.get("article_url", ""),
            ))
    
    response_data = {"answer": answer, "sources": [s.model_dump() for s in sources]}
    
    # Сохранение в истории и кеширование
    cache.set(request.question, response_data)
    analytics.log_interaction(request.question, answer, chunks, p_time)
    
    return response_data


# --- Admin endpoints ---

@app.post("/admin/clear")
async def admin_clear():
    """Полностью очищает базу знаний (удаляет все чанки)."""
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, pipeline.hybrid_search.clear_collection)
        pipeline._cached_search.cache_clear()
        count = pipeline.hybrid_search.client.count(
            collection_name=pipeline.hybrid_search.collection_name
        ).count
        logging.info("Knowledge base cleared.")
        return {"status": "ok", "chunks_remaining": count}
    except Exception as e:
        logging.error(f"admin/clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/documents")
async def admin_list_documents():
    """Возвращает список документов, загруженных в базу знаний."""
    try:
        loop = asyncio.get_event_loop()
        titles = await loop.run_in_executor(None, pipeline.hybrid_search.list_documents)
        return {"documents": titles, "count": len(titles)}
    except Exception as e:
        logging.error(f"admin/documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DeleteDocumentRequest(BaseModel):
    title: str


@app.post("/admin/delete-document")
async def admin_delete_document(request: DeleteDocumentRequest):
    """Удаляет все чанки конкретного документа по его названию (title)."""
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, pipeline.hybrid_search.delete_by_document, request.title)
        pipeline._cached_search.cache_clear()
        total = pipeline.hybrid_search.client.count(
            collection_name=pipeline.hybrid_search.collection_name
        ).count
        logging.info(f"Deleted document '{request.title}'. Chunks remaining: {total}")
        return {"status": "ok", "deleted_title": request.title, "chunks_remaining": total}
    except Exception as e:
        logging.error(f"admin/delete-document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/update")
async def admin_update(file: UploadFile = File(...)):
    """Обновляет документы из файла: удаляет старые чанки с совпадающим title, загружает новые.
    Остальные документы в базе не затрагиваются."""
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("md", "json"):
        raise HTTPException(status_code=400, detail="Принимаются только файлы .md и .json")

    try:
        raw = await file.read()
        content = raw.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось прочитать файл: {e}")

    try:
        chunks = parse_file(filename, content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Ошибка разбора файла: {e}")

    if not chunks:
        raise HTTPException(status_code=422, detail="Чанки не найдены. Проверьте формат файла.")

    titles_in_file = {c["title"] for c in chunks}

    try:
        loop = asyncio.get_event_loop()
        for title in titles_in_file:
            await loop.run_in_executor(None, pipeline.hybrid_search.delete_by_document, title)
        added = await loop.run_in_executor(None, pipeline.hybrid_search.upload_chunks, chunks)
        pipeline._cached_search.cache_clear()
        total = pipeline.hybrid_search.client.count(
            collection_name=pipeline.hybrid_search.collection_name
        ).count
        logging.info(f"Updated {list(titles_in_file)}: {added} chunks. Total: {total}")
        return {
            "status": "ok",
            "updated_documents": sorted(titles_in_file),
            "added": added,
            "total": total,
        }
    except Exception as e:
        logging.error(f"admin/update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/upload")
async def admin_upload(file: UploadFile = File(...)):
    """Загружает MD или JSON файл и добавляет чанки в базу знаний."""
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("md", "json"):
        raise HTTPException(status_code=400, detail="Принимаются только файлы .md и .json")

    try:
        raw = await file.read()
        content = raw.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось прочитать файл: {e}")

    try:
        chunks = parse_file(filename, content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Ошибка разбора файла: {e}")

    if not chunks:
        raise HTTPException(status_code=422, detail="Чанки не найдены. Проверьте формат файла.")

    try:
        loop = asyncio.get_event_loop()
        added = await loop.run_in_executor(None, pipeline.hybrid_search.upload_chunks, chunks)
        pipeline._cached_search.cache_clear()
        total = pipeline.hybrid_search.client.count(
            collection_name=pipeline.hybrid_search.collection_name
        ).count
        logging.info(f"Uploaded {added} chunks from {filename}. Total: {total}")
        return {"status": "ok", "added": added, "total": total}
    except Exception as e:
        logging.error(f"admin/upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
