#!/bin/bash
echo -n "$FLAG" > /flag.txt
chmod 644 /flag.txt
exec "$@"
