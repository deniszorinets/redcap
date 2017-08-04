#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
    CREATE USER "${VAULT_USER}" WITH LOGIN PASSWORD '${VAULT_PASS}';
    CREATE DATABASE vault OWNER "${VAULT_USER}";
    CREATE USER "${REDCAP_USER}" WITH LOGIN PASSWORD '${REDCAP_PASS}';
    CREATE DATABASE redcap OWNER "${VAULT_USER}";
EOSQL

psql -v ON_ERROR_STOP=1 --username "${VAULT_USER}" <<-EOSQL
    CREATE TABLE vault_kv_store (parent_path TEXT COLLATE "C" NOT NULL, path TEXT COLLATE "C", key TEXT COLLATE "C", value BYTEA, CONSTRAINT pkey PRIMARY KEY (path, key));
    CREATE INDEX parent_path_idx ON vault_kv_store (parent_path);
EOSQL
