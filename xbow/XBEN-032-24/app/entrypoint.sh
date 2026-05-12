#!/bin/bash
echo -n "$FLAG" > /app/flag.txt
exec "$@"
