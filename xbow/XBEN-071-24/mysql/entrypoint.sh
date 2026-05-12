#!/bin/bash

# Replace FLAG placeholder at runtime
sed -i "s/\${FLAG}/${FLAG}/g" /docker-entrypoint-initdb.d/backup.sql

# Delegate to the original MySQL entrypoint
exec docker-entrypoint.sh "$@"
