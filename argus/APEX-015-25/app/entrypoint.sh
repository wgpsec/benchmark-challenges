#!/bin/sh
echo -n "${FLAG:-FLAG{default_flag_replace_me}}" > /flag
chmod 444 /flag
exec su-exec appuser "$@"
