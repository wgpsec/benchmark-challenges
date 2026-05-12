#!/bin/bash
set -e

# Inject FLAG at runtime (replaces build-time sed)
sed -i "s/FLAG/$FLAG/g" /app/flag.txt

exec "$@"
