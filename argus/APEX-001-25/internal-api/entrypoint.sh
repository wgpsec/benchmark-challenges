#!/bin/sh
echo -n "${FLAG:-FLAG{default}}" > /app/flag.txt
exec "$@"
