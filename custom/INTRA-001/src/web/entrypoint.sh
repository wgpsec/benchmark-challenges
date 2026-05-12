#!/bin/bash
echo -n "${FLAG:-FLAG{command_injection_rce_success}}" > /flag.txt
exec "$@"
