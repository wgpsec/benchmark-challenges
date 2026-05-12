#!/bin/bash
set -e

# Inject flag at runtime
if [ -n "$FLAG" ]; then
    sed -i "s/FLAG_PLACEHOLDER/$FLAG/g" /docker-entrypoint-initdb.d/init.sql
fi

# Execute the original MySQL entrypoint
exec docker-entrypoint.sh "$@"
