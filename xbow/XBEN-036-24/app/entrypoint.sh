#!/bin/bash
sed -i "s/FLAG/$FLAG/g" /app/flag.txt
exec "$@"
