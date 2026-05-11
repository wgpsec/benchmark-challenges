FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=password

ARG FLAG
ADD init.sql /docker-entrypoint-initdb.d
RUN sed -i s/FLAG_PLACEHOLDER/$FLAG/g /docker-entrypoint-initdb.d/init.sql

EXPOSE 3306
CMD ["mysqld", "--default-authentication-plugin=mysql_native_password"]
