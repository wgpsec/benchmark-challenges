#!/bin/bash
echo -n "${FLAG:-flag{default}}" > /var/www/lfi_static_resource/app/static/flag
exec "$@"
