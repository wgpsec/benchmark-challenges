#!/bin/bash
echo -n "$FLAG" > /flag.txt
chmod 644 /flag.txt

mkdir -p /var/spool/cron/crontabs
crond

# Load initial keys after redis is ready (background)
(sleep 2 && /init.sh) &

# Start redis in foreground as PID 1
exec redis-server --protected-mode no --bind 0.0.0.0
