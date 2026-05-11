FROM php:7.4-apache

RUN echo "deb [trusted=yes] http://archive.debian.org/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://archive.debian.org/debian-security/ buster/updates main" >> /etc/apt/sources.list

EXPOSE 80

RUN apt-get update -y

RUN apt-get install -y curl

COPY . /var/www/html/
