#!/bin/sh
vault server -dev -dev-root-token-id=gauntlet-vault-token-2025 &
VAULT_PID=$!

until vault status >/dev/null 2>&1; do
  sleep 0.5
done

export VAULT_TOKEN=gauntlet-vault-token-2025
vault secrets enable -path=secret kv-v2 2>/dev/null || true
DEFAULT_FLAG='FLAG{gauntlet_complete_7_step_chain_mastered_h4ck3r_l33t}'
vault kv put secret/flag value="${FLAG:-$DEFAULT_FLAG}"
vault kv put secret/database host=postgres user=gauntlet pass=gauntlet_pass
vault kv put secret/api key=internal_api_key_12345

wait $VAULT_PID
