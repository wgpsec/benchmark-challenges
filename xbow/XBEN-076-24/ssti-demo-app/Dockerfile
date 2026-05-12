FROM python:3.9-slim

RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true

WORKDIR /app

COPY . /app

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN apt-get update -y && apt-get install -y curl

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
