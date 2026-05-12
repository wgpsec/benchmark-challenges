#!/bin/sh

echo -n "${FLAG:-FLAG{default}}" > /flag
chmod 400 /flag
chown nodejs:nodejs /flag

exec su-exec nodejs "$@"
