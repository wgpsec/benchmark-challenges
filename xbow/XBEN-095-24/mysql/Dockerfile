FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=password
ADD init.sql /docker-entrypoint-initdb.d

EXPOSE 3306
CMD ["mysqld", "--default-authentication-plugin=mysql_native_password"]
