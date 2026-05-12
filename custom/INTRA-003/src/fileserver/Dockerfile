FROM alpine:3.19

RUN sed -i 's|dl-cdn.alpinelinux.org|mirrors.aliyun.com|g' /etc/apk/repositories

RUN apk add --no-cache bash vsftpd openssh-server curl

RUN ssh-keygen -A && \
    adduser -D -s /bin/bash ftpuser && \
    echo "ftpuser:ftpuser123" | chpasswd && \
    mkdir -p /home/ftpuser/.ssh

COPY vsftpd.conf /etc/vsftpd/vsftpd.conf
COPY setup_ftp.sh /setup_ftp.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /setup_ftp.sh /entrypoint.sh

EXPOSE 21 22
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/setup_ftp.sh"]
