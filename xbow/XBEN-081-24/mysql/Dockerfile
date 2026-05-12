FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=password

ADD init.sql /docker-entrypoint-initdb.d
COPY entrypoint.sh /usr/local/bin/custom-entrypoint.sh
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

EXPOSE 3306
ENTRYPOINT ["custom-entrypoint.sh"]
CMD ["mysqld", "--default-authentication-plugin=mysql_native_password"]
