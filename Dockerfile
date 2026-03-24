FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/data/jobs

WORKDIR /app

COPY requirements.txt ./
COPY pyproject.toml ./
COPY README.md ./
COPY api ./api
COPY frontend ./frontend
COPY paperflow_postprocess ./paperflow_postprocess

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install .

EXPOSE 8000

VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
