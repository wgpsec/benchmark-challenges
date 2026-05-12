FROM debian:bullseye-slim

RUN [ -f /etc/apt/sources.list ] && sed -i "s|deb.debian.org|mirrors.aliyun.com|g" /etc/apt/sources.list || true
RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/deserialization_pickle_bookmarks/app/requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /var/www/deserialization_pickle_bookmarks/app/requirements.txt

COPY ./deserialization_pickle_bookmarks-httpd.conf /etc/apache2/sites-available/deserialization_pickle_bookmarks-httpd.conf
COPY ./website/deserialization_pickle_bookmarks.wsgi /var/www/deserialization_pickle_bookmarks/
COPY ./website/run.py /var/www/deserialization_pickle_bookmarks/
COPY ./website/app /var/www/deserialization_pickle_bookmarks/app
RUN chown -R www-data.www-data /var/www/deserialization_pickle_bookmarks/app/

RUN a2dissite 000-default.conf
RUN a2ensite deserialization_pickle_bookmarks-httpd.conf
RUN a2enmod headers

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]