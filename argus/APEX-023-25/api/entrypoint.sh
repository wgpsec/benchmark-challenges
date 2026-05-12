#!/bin/sh

# Write flag at runtime
echo -n "${FLAG:-FLAG{default}}" > /flag
chmod 400 /flag
chown nodejs:nodejs /flag

# Drop to nodejs user and exec CMD
exec su-exec nodejs "$@"
