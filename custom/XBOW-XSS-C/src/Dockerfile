FROM python:2.7-slim-stretch

RUN echo "deb [trusted=yes] http://mirrors.aliyun.com/debian-archive/debian/ stretch main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://mirrors.aliyun.com/debian-archive/debian-security/ stretch/updates main" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]

EXPOSE 80
