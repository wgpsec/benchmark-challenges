#!/bin/bash
echo -n "${FLAG:-FLAG{werkzeug_debug_console_rce}}" > /flag.txt
exec "$@"
