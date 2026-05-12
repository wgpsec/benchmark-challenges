FROM mysql:8.0
COPY backup.sql /docker-entrypoint-initdb.d/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["mysqld"]
