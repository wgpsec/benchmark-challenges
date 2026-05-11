FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=idor_custom_authn_header_trading_platform
ENV MYSQL_DATABASE=database

EXPOSE 3306
CMD ["mysqld", "--default-authentication-plugin=mysql_native_password"]
