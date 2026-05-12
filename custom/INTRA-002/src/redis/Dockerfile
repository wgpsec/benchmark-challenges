FROM redis:7-alpine

RUN sed -i 's|dl-cdn.alpinelinux.org|mirrors.aliyun.com|g' /etc/apk/repositories
RUN apk add --no-cache bash coreutils dcron

COPY entrypoint.sh /entrypoint.sh
COPY init.sh /init.sh
RUN chmod +x /entrypoint.sh /init.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["redis-server", "--protected-mode", "no", "--bind", "0.0.0.0"]
