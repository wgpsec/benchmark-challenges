FROM hashicorp/vault:1.15

COPY config.json /vault/config/config.json
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV VAULT_ADDR=http://127.0.0.1:8200

ENTRYPOINT ["/entrypoint.sh"]
