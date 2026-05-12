#!/bin/bash
echo -n "${FLAG:-FLAG{php_upload_bypass_pht}}" > /flag.txt
exec "$@"
