FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com requests

COPY bot.py .

CMD ["python", "-u", "bot.py"]
