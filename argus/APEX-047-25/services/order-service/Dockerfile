FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl wget && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3002
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3002"]
