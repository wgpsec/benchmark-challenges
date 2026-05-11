FROM php:7.4-apache

RUN [ -f /etc/apt/sources.list ] && sed -i "s|deb.debian.org|mirrors.aliyun.com|g" /etc/apt/sources.list || true
RUN apt-get update -y

RUN apt-get install -y curl libcurl4-openssl-dev pkg-config

RUN docker-php-ext-install curl

COPY . /var/www/html/

EXPOSE 80
