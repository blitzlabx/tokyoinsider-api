# Blitz TokyoInsider Scraper API
# Author: Blitz (@blitzlabx)
# https://github.com/blitzlabx/tokyoinsider-api

FROM python:3.12-slim

WORKDIR /app

# System deps for lxml / curl_cffi
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PORT=8000
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Render / Railway inject $PORT — use shell form so it expands
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
