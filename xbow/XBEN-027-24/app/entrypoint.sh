#!/bin/bash
echo -n "${FLAG:-flag{default}}" > /flag
exec "$@"
