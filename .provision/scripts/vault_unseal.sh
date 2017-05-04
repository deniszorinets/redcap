#!/usr/bin/env bash

export VAULT_ADDR=http://127.0.0.1:8200
UNSEAL_KEY1=$(awk '/Unseal Key 1: (.*)/{print $4}' /etc/vault/keys)
UNSEAL_KEY2=$(awk '/Unseal Key 2: (.*)/{print $4}' /etc/vault/keys)
UNSEAL_KEY3=$(awk '/Unseal Key 3: (.*)/{print $4}' /etc/vault/keys)
vault unseal $UNSEAL_KEY1
vault unseal $UNSEAL_KEY2
vault unseal $UNSEAL_KEY3
