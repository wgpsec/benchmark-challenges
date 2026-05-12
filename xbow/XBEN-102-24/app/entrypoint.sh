#!/bin/bash
set -e

# Inject FLAG at runtime
if [ -n "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" /app/app.py
fi

exec "$@"
