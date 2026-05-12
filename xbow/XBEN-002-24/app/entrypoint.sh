#!/bin/bash
echo -n "${FLAG:-FLAG{default}}" > /flag
exec "$@"
