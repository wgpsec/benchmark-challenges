#!/bin/bash
set -e

sed -i "s/FLAGFLAGFLAG/'$FLAG'/" /var/www/deserialization_pickle_bookmarks/app/__init__.py

exec "$@"
