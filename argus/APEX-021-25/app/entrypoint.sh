#!/bin/sh

# Write flag file at runtime (as root)
echo -n "${FLAG:-FLAG{default_flag_replace_me}}" > /flag
chmod 444 /flag

# Drop privileges and exec CMD as nodejs user
exec su-exec nodejs "$@"
