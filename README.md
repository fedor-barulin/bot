# Enterprise RAG AI Support Agent — Телеком AI-Ассистент

## Описание проекта

Система уровня Enterprise для автоматизации технической поддержки сотрудников оператора связи. Бот отвечает строго на основе загруженных внутренних документов (PDF-чанков), не выдумывает факты и всегда ссылается на источник из базы знаний.

### Ключевые возможности

| Компонент | Описание |
|---|---|
| **Query Understanding** | Определяет интент, затронутый сервис и тип проблемы |
| **Knowledge Routing** | Маршрутизирует запрос в нужный раздел базы знаний |
| **Query Rewriting** | Переформулирует вопрос несколькими способами через LLM для полноты поиска |
| **Hybrid Search** | Векторный поиск через Qdrant + модель `BAAI/bge-m3` |
| **Cross-Encoder Reranking** | Пересортировка результатов через `BAAI/bge-reranker-large` |
| **Reasoning Engine** | LLM формирует структурированный ответ: объяснение → причины → диагностика → решение |
| **Anti-Hallucination** | Если факта нет в базе — система строго отвечает «Информация отсутствует в базе знаний» |
| **Кеширование** | Redis хранит ответы на повторяющиеся запросы |
| **Аналитика** | Логирование взаимодействий в `analytics.log` |

---

## Технологический стек

- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic
- **Vector DB**: Qdrant (серверный или локальный disk-режим)
- **Embeddings**: `BAAI/bge-m3` via SentenceTransformers
- **Reranker**: `BAAI/bge-reranker-large` via FlagEmbedding
- **LLM**: `g4f` — бесплатные провайдеры (GPT-4 / Llama3), без GPU и API-ключей
- **Cache**: Redis (опционально, система работает и без него)
- **Frontend**: React 18, Axios
- **Инфраструктура**: Docker, Docker Compose

---

## Структура репозитория

```
.
├── backend/                  # RAG-пайплайн и FastAPI API
│   ├── main.py               # Точка входа API (/chat endpoint)
│   ├── rag_pipeline.py       # Оркестрация всего пайплайна
│   ├── hybrid_search.py      # Векторный поиск в Qdrant
│   ├── reranker.py           # Cross-encoder реранкинг
│   ├── llm_client.py         # Клиент g4f для LLM
│   ├── query_understanding.py
│   ├── query_rewriter.py
│   ├── knowledge_router.py
│   ├── context_builder.py
│   ├── reasoning_engine.py
│   ├── answer_validator.py
│   ├── cache.py              # Redis-кеш
│   ├── analytics.py          # Логирование
│   └── requirements.txt
├── frontend/
│   └── chat_ui/              # React-чат (Create React App)
├── data/
│   ├── upload_markdown.py    # Скрипт загрузки чанков в базу знаний
│   ├── example_upload.py     # Пример программной загрузки одного чанка
│   └── qdrant_storage/       # Локальное хранилище Qdrant (disk-режим)
└── infra/
    ├── Dockerfile            # Docker-образ бэкенда
    └── docker-compose.yml    # Backend + Qdrant + Redis
```

---

## Деплой через Docker

### Требования

- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js / npm](https://nodejs.org/) — для запуска фронтенда

### Шаг 1 — Запустить инфраструктуру

```bash
cd infra
docker-compose up -d --build
```

Это поднимет три сервиса:

| Сервис | Порт | Описание |
|---|---|---|
| `backend` | `8000` | FastAPI RAG API |
| `qdrant` | `6333` | Векторная база данных |
| `redis` | `6379` | Кеш популярных запросов |

Первая сборка займёт несколько минут — внутри Docker-образа скачивается модель `BAAI/bge-m3` (~2.2 ГБ).

Проверить, что всё работает:
```bash
curl http://localhost:8000/docs
```

### Шаг 2 — Наполнить базу знаний

Пока контейнеры работают, загрузите документы. Qdrant доступен с хост-машины на `localhost:6333`:

```bash
pip install qdrant-client sentence-transformers
python data/upload_markdown.py data/my_documents.md --qdrant-host localhost
```

Подробнее про формат файлов и скрипт — в разделе [Наполнение базы знаний](#наполнение-базы-знаний) ниже.

### Шаг 3 — Запустить фронтенд

```bash
cd frontend/chat_ui
npm install
npm start
```

Откройте в браузере: [http://localhost:3000](http://localhost:3000)

### Переменные окружения

Настраиваются в `infra/docker-compose.yml` для сервиса `backend`:

| Переменная | По умолчанию | Описание |
|---|---|---|
| `QDRANT_HOST` | `qdrant` | Хост Qdrant-сервера |
| `REDIS_HOST` | `redis` | Хост Redis |
| `LLM_MODEL` | `llama3` | Модель для g4f |

---

## Наполнение базы знаний

### Формат файла

Скрипт `data/upload_markdown.py` принимает markdown-файлы, где каждый чанк имеет следующую структуру:

```markdown
### [Название файла.pdf] Раздел: Название раздела (Стр. N)
**Теги:** тег1, тег2

Текст чанка — произвольный текст из документа, который будет
векторизован и загружен в базу знаний...

---
```

- **Заголовок** — название PDF-файла, раздел и номер страницы
- **Теги** — список через запятую или `нет` если тегов нет
- **Текст** — содержимое чанка (может быть многострочным)
- **Разделитель** — строка `---` между чанками

### Загрузка файлов

**Локальный режим** (disk-хранилище, Qdrant-сервер не нужен):
```bash
python data/upload_markdown.py data/my_file.md
```

**Docker / серверный режим** (подключение к запущенному Qdrant):
```bash
python data/upload_markdown.py data/my_file.md --qdrant-host localhost
# Нестандартный порт:
python data/upload_markdown.py data/my_file.md --qdrant-host localhost --qdrant-port 6333
```

**Через переменную окружения:**
```bash
QDRANT_HOST=localhost python data/upload_markdown.py data/my_file.md
```

При первом запуске скрипт скачает модель `BAAI/bge-m3` (~2.2 ГБ). При повторных запусках модель берётся из кеша.

Скрипт автоматически создаёт коллекцию `knowledge_base` в Qdrant, если она ещё не существует, и дополняет её — повторный запуск с другим файлом добавляет новые чанки, не стирая старые.

### Программная загрузка одного чанка

Для загрузки отдельных чанков вручную или из своего скрипта смотрите пример `data/example_upload.py`:

```python
chunk = {
    "chunk_id": 1,
    "title": "Мобильный интернет",
    "section": "Подключение",
    "text": "Подключение услуги выполняется USSD *104*18#...",
    "tags": ["internet", "activation"],
    "source": "mobile_internet.pdf",
    "page": 3
}
```

---

## Как работает RAG-пайплайн

При каждом запросе пользователя система проходит 8 шагов:

```
Вопрос пользователя
       │
       ▼
1. Query Understanding   — определить интент, сервис, тип проблемы
       │
       ▼
2. Knowledge Routing     — выбрать нужные разделы базы знаний
       │
       ▼
3. Query Rewriting       — переформулировать вопрос несколькими способами (LLM)
       │
       ▼
4. Hybrid Search         — векторный поиск по всем вариантам вопроса (Qdrant)
       │
       ▼
5. Cross-Encoder Rerank  — отобрать ТОП-5 наиболее релевантных чанков
       │
       ▼
6. Context Building      — собрать контекст из отобранных чанков
       │
       ▼
7. Reasoning Engine      — сгенерировать структурированный ответ (LLM)
       │
       ▼
8. Answer Validation     — проверить ответ на галлюцинации
       │
       ▼
Ответ + ссылки на источники
```

Redis-кеш проверяется перед шагом 1 — если вопрос уже встречался, ответ возвращается мгновенно.
