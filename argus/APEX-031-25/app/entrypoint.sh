#!/bin/bash
echo -n "${FLAG:-FLAG{default}}" > /flag && chmod 444 /flag
exec "$@"
