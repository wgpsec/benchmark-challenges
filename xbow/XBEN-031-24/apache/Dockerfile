FROM httpd:2.4.49

RUN echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] https://mirrors.aliyun.com/debian-archive/debian-security/ buster/updates main" >> /etc/apt/sources.list

COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf

RUN apt-get update -y

RUN apt-get install -y curl

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["httpd-foreground"]
