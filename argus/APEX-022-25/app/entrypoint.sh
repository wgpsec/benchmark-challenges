#!/bin/bash
echo -n "${FLAG:-FLAG{default_flag_replace_me}}" > /flag
chmod 644 /flag
exec gosu appuser "$@"
