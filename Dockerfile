FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads outputs

EXPOSE 8501

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}