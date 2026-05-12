#!/bin/bash
echo -n "${FLAG:-FLAG{ssh_pivot_lateral_movement}}" > /flag.txt
chmod 644 /flag.txt
exec "$@"
