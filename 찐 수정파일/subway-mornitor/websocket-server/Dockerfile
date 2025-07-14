FROM python:3.10-slim

WORKDIR /app

COPY websocket_server.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "websocket_server:app", "--host", "0.0.0.0", "--port", "8001"]
