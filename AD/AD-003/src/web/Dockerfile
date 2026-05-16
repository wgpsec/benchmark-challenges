FROM python:3.11-slim

RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install flask requests -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

WORKDIR /app
COPY app.py .
COPY templates/ templates/
COPY config/ config/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
