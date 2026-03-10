# Telecom AI Support Agent

## Project Overview

Enterprise RAG (Retrieval-Augmented Generation) AI support system designed for a telecom operator's internal knowledge base. Employees can ask technical questions and get answers sourced from internal documents.

## Architecture

- **Frontend**: React (Create React App) — `frontend/chat_ui/` — runs on port 5000
- **Backend**: FastAPI — `backend/` — runs on port 8000
- **Vector DB**: Qdrant (external service)
- **Cache**: Redis (external service)
- **LLM**: g4f (free LLM providers)

## Key Features

- Query understanding (intent, service, problem type detection)
- Knowledge routing to reduce search noise
- Query rewriting via LLM
- Hybrid vector search with Qdrant + BAAI/bge-m3 embeddings
- Cross-encoder reranking with BAAI/bge-reranker-large
- Answer validation (anti-hallucination)
- Redis caching for frequent queries

## Setup & Configuration

### Frontend
- Runs on `0.0.0.0:5000`
- `DANGEROUSLY_DISABLE_HOST_CHECK=true` set in `.env` to allow Replit proxy
- Proxies `/api` requests to backend at `http://localhost:8000`
- API calls use relative URL `/api/chat` (not hardcoded localhost)

### Backend
- FastAPI app in `backend/main.py`
- Requires Qdrant and Redis to be running externally
- Environment variables: `QDRANT_HOST`, `REDIS_HOST`, `LLM_MODEL`
- CORS is fully open (`allow_origins=["*"]`)

### Workflow
- **Start application**: `cd frontend/chat_ui && npm start`
- Port: 5000 (webview)

### Deployment
- Target: static
- Build: `cd frontend/chat_ui && npm run build`
- Public dir: `frontend/chat_ui/build`

## File Structure

```
backend/          - FastAPI RAG pipeline components
frontend/chat_ui/ - React chat UI
data/             - Example scripts for uploading knowledge chunks
infra/            - Docker Compose & Dockerfile (for local deployment)
```

## Notes

- Backend requires external Qdrant + Redis services to function (not available in Replit by default)
- For full functionality, set `QDRANT_HOST` and `REDIS_HOST` environment variables
- Data upload script: `python data/example_upload.py`
