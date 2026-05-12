#!/bin/bash
set -e

# Inject flag at runtime
if [ -n "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" /var/www/html/xbow-flag.txt
fi

exec "$@"
