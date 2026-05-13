FROM haproxy:2.0.5

RUN echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian-security/ buster/updates main" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y curl 

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg