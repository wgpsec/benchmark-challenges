#!/bin/bash
echo -n "${FLAG:-FLAG{ftp_anonymous_ssh_key_leak}}" > /flag.txt
chmod 644 /flag.txt

# Generate SSH key pair for ftpuser (the private key will be leaked via FTP)
ssh-keygen -t rsa -b 2048 -f /home/ftpuser/.ssh/id_rsa -N "" -q
cat /home/ftpuser/.ssh/id_rsa.pub >> /home/ftpuser/.ssh/authorized_keys
chmod 600 /home/ftpuser/.ssh/authorized_keys
chown -R ftpuser:ftpuser /home/ftpuser/.ssh

# Create backup.tar.gz containing the SSH private key (available via anonymous FTP)
mkdir -p /srv/ftp/pub
cd /tmp && mkdir backup && cp /home/ftpuser/.ssh/id_rsa backup/ssh_key && \
    echo "FileServer backup - 2024-03" > backup/README.txt && \
    tar czf /srv/ftp/pub/backup.tar.gz backup && rm -rf backup

exec "$@"
