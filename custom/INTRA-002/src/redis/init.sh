#!/bin/bash
# Set the readable flag as a redis key (this is what SSRF can read)
redis-cli SET flag "${FLAG_READABLE:-FLAG{ssrf_redis_key_leaked}}"
redis-cli SET admin_note "Internal cache - do not expose externally"
