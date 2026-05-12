FROM mongo:7.0

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/

# Flag will be passed to the app, not stored in Mongo directly

EXPOSE 27017

CMD ["mongod", "--bind_ip_all"]
