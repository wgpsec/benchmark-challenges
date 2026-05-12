FROM python:3.9-slim

RUN [ -f /etc/apt/sources.list ] && sed -i "s|deb.debian.org|mirrors.aliyun.com|g" /etc/apt/sources.list || true
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl procps\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . /app
RUN chmod +x app/check_service.sh

WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
