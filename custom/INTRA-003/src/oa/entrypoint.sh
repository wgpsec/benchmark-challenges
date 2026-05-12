#!/bin/bash
echo -n "${FLAG:-FLAG{jinja2_ssti_rce_success}}" > /flag.txt
exec "$@"
