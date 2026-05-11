FROM python:3.11-slim
WORKDIR /app
RUN sed -i "s|deb.debian.org|mirrors.aliyun.com|g" /etc/apt/sources.list.d/debian.sources 2>/dev/null; sed -i "s|deb.debian.org|mirrors.aliyun.com|g" /etc/apt/sources.list 2>/dev/null || true

RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
COPY . .
RUN mkdir -p certs && \
    openssl req -x509 -newkey rsa:2048 -keyout certs/idp-key.pem -out certs/idp-cert.pem \
    -days 365 -nodes -subj '/CN=FederAuth IdP/O=APEX Benchmark/C=US'
EXPOSE 5000
CMD ["python", "app.py"]
