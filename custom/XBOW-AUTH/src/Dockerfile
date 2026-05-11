FROM php:5-apache

RUN echo "deb [trusted=yes] http://archive.debian.org/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://archive.debian.org/debian-security/ buster/updates main" >> /etc/apt/sources.list

RUN a2enmod rewrite

COPY . /var/www/html/
WORKDIR /var/www/html

COPY apache.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80
