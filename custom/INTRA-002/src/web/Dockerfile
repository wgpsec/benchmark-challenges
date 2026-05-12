FROM python:3.11-slim

RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null; \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null; true

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com flask requests

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
