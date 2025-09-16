FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend backend

ENV PYTHONUNBUFFERED=1

CMD ["flask", "--app", "backend.app", "run", "--host=0.0.0.0", "--port", "5000"]
