FROM php:7.4-apache

RUN echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian-security/ buster/updates main" >> /etc/apt/sources.list

EXPOSE 80

RUN apt-get update -y

RUN apt-get install -y curl

COPY . /var/www/html/
