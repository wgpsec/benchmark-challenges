#!/bin/sh

# Write flag at runtime
echo -n "${FLAG:-FLAG{default_flag_replace_me}}" > /flag
chmod 444 /flag

# Drop to nodejs user and exec CMD
exec su-exec nodejs "$@"
