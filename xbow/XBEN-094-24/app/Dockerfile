
FROM python:3.9-slim-buster

RUN echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian-security/ buster/updates main" >> /etc/apt/sources.list

WORKDIR /app

RUN apt-get update && apt-get install -y curl

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .


CMD ["python", "app.py"]
