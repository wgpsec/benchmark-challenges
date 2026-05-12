#!/bin/bash
set -e

# Inject flag at runtime
sed -i "s/@FLAG@/${FLAG}/g" /var/www/flag.txt

exec "$@"
