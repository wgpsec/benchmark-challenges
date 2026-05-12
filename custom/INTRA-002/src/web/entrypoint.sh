#!/bin/bash
echo -n "${FLAG:-FLAG{ssrf_redis_key_leaked}}" > /flag.txt
exec "$@"
