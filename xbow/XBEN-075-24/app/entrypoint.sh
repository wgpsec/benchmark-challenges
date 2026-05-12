#!/bin/bash
set -e

# Inject flag at runtime
if [ -n "$FLAG" ]; then
    sed -i "s/FLAGFLAGFLAG/'$FLAG'/" /var/www/deserialization_yaml_bookmarks/app/__init__.py
fi

exec "$@"
