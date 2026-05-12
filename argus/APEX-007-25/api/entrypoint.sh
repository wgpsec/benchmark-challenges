#!/bin/sh
echo -n "${FLAG:-FLAG{default_flag_replace_me}}" > /flag.txt
exec "$@"
