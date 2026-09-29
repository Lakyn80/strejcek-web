# syntax=docker/dockerfile:1.7

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY --from=cz-accounting-module /packages/accounting-api /tmp/accounting-api
COPY requirements.txt .
RUN sed "/^accounting-api/d" requirements.txt > requirements-docker.txt \
    && pip install --no-cache-dir "/tmp/accounting-api[production]" \
    && pip install --no-cache-dir -r requirements-docker.txt

COPY app ./app
COPY assets ./assets

EXPOSE 8000

CMD ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
