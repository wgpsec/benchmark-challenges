FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN mkdir -p /app/config
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY parser.py ./
EXPOSE 3003
CMD ["python", "parser.py"]
