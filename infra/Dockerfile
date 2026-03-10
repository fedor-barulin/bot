FROM python:3.14-rc-slim

WORKDIR /app

# Устанавливаем системные зависимости для сборки библиотек
RUN apt-get update && apt-get install -y build-essential

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Установка модели внутри докер-образа для локального кэша
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

COPY . /app/
ENV PYTHONPATH=/app
