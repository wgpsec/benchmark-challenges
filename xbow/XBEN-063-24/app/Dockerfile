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

COPY ./website/requirements.txt /var/www/ssti_encoding_loan_calculator/app/requirements.txt
RUN pip install -r /var/www/ssti_encoding_loan_calculator/app/requirements.txt

COPY ./ssti_encoding_loan_calculator-httpd.conf /etc/apache2/sites-available/ssti_encoding_loan_calculator-httpd.conf
COPY ./website/ssti_encoding_loan_calculator.wsgi /var/www/ssti_encoding_loan_calculator/
COPY ./website/run.py /var/www/ssti_encoding_loan_calculator/
COPY ./website/app /var/www/ssti_encoding_loan_calculator/app

RUN a2dissite 000-default.conf
RUN a2ensite ssti_encoding_loan_calculator-httpd.conf
RUN a2enmod headers

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD  ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]