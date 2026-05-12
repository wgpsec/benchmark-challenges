#!/bin/bash
set -e

sed -i "s/FLAG/$FLAG/g" /app/flag.txt

exec "$@"
