#!/bin/bash
echo -n "${FLAG:-FLAG{default}}" > /var/www/flag.txt
chmod 644 /var/www/flag.txt
exec "$@"
