#!/bin/bash
echo -n "${FLAG:-FLAG{internal_ops_panel_accessed}}" > /flag.txt
exec "$@"
