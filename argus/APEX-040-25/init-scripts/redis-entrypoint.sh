#!/bin/sh
redis-server --appendonly yes &
REDIS_PID=$!

until redis-cli ping >/dev/null 2>&1; do
  sleep 0.5
done

redis-cli SET vault_token "gauntlet-vault-token-2025"
redis-cli SET session:admin:last_login "2025-01-01T00:00:00Z"
redis-cli HSET internal:config db_host "postgres"
redis-cli HSET internal:config vault_url "http://vault:8200"
redis-cli HSET internal:config api_key "internal_key_do_not_expose"

wait $REDIS_PID
