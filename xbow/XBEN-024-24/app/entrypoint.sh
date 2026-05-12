#!/bin/bash
sed -i "s/@FLAG@/$FLAG/g" /app/app.py
exec "$@"
