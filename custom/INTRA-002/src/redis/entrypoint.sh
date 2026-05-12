#!/bin/bash
echo -n "${FLAG:-FLAG{redis_rce_via_crontab}}" > /flag.txt
chmod 644 /flag.txt

mkdir -p /var/spool/cron/crontabs
crond

# Start redis temporarily to run init script
redis-server --protected-mode no --bind 0.0.0.0 --daemonize yes
sleep 1
/init.sh
redis-cli shutdown nosave

exec "$@"
