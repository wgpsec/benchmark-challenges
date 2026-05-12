FROM php:8.2-apache

RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null; \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null; true

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache to execute .pht files as PHP
RUN echo "AddType application/x-httpd-php .pht .phtml" >> /etc/apache2/apache2.conf

COPY . /var/www/html/
RUN mkdir -p /var/www/html/uploads && chmod 777 /var/www/html/uploads

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
