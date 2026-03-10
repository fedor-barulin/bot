# Telecom AI Support Agent

## Project Overview

Enterprise RAG (Retrieval-Augmented Generation) AI support system for a telecom operator's internal knowledge base. Employees ask technical questions and get answers sourced from internal documents.

## Architecture

- **Frontend**: React (Create React App) — `frontend/chat_ui/` — port 5000
- **Backend**: FastAPI — `backend/` — port 8000
- **Vector DB**: Qdrant in local disk mode at `data/qdrant_storage/` (no external server needed)
- **Cache**: Redis (optional — fails gracefully if not running)
- **LLM**: g4f (free LLM providers, no API key needed)
- **Embeddings**: BAAI/bge-m3 (lazy-loaded on first query)
- **Reranker**: BAAI/bge-reranker-large (lazy-loaded on first query)

## Key Features

- Query understanding (intent, service, problem type)
- Knowledge routing to reduce search noise
- Query rewriting via LLM
- Hybrid vector search with local Qdrant + BAAI/bge-m3 embeddings
- Cross-encoder reranking with BAAI/bge-reranker-large
- Answer validation (anti-hallucination)
- Redis caching for frequent queries (optional)

## Knowledge Base

- Stored in `data/qdrant_storage/` (local Qdrant format)
- Collection: `knowledge_base`, vector size: 1024, distance: COSINE
- **To add new files**: run `python data/upload_markdown.py <path_to_markdown_file>`
- Uploaded markdown format: `### [file.pdf] Раздел: Section (Стр. N)` + `**Теги:** ...` + content

## Current Knowledge Base Contents

- `Свой тариф_СО.pdf` — 7 chunks (tariff info, conditions, costs, restrictions)
- `Мобильный Интернет.pdf` — 3 chunks (mobile internet setup, settings, cost)
- `Контакты МОТИВ.pdf` — 1 chunk (contacts and support numbers)
- `Вспомогательные сервисные номера.pdf` — 1 chunk (USSD/SMS service numbers)

## Workflows

- **Start application**: `cd frontend/chat_ui && npm start` — port 5000 (webview)
- **Start Backend**: `cd backend && python -m uvicorn main:app --host localhost --port 8000` — port 8000 (console)

## Frontend Setup

- Runs on `0.0.0.0:5000`
- `DANGEROUSLY_DISABLE_HOST_CHECK=true` in `.env` to allow Replit proxy
- Proxies `/chat` requests to backend at `http://localhost:8000` via `package.json` proxy field

## Backend Setup

- FastAPI app in `backend/main.py`
- Uses local Qdrant storage by default (no `QDRANT_HOST` env var needed)
- Set `QDRANT_HOST` env var to point to an external Qdrant server if needed
- ML models load lazily on first request (not at startup) to avoid slow boot

## Deployment

- Target: static (React build)
- Build: `cd frontend/chat_ui && npm run build`
- Public dir: `frontend/chat_ui/build`
