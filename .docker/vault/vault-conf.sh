#!/bin/sh

cat > /vault/config/vault.json <<EOL
storage "postgresql" {
    connection_url = "postgres://vault:${VAULT_PASS}@db:5432/vault?sslmode=disable"
}

listener "tcp" {
    address     = "0.0.0.0:8200"
    tls_disable = 1
}
EOL
