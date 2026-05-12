#!/bin/bash

# Write flag file at runtime (as root)
echo -n "${FLAG:-FLAG{placeholder}}" > /flag
chmod 444 /flag

# Drop privileges and exec the CMD
exec gosu appuser "$@"
