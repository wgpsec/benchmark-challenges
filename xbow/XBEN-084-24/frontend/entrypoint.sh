#!/bin/sh
set -e

sed -i "s/@FLAG@/$FLAG/g" /app/.env

exec "$@"
