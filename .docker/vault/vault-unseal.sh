#!/bin/sh

UNSEAL_KEY1=$(awk '/Unseal Key 1: (.*)/{print $4}' /vault/keys/secret)
UNSEAL_KEY2=$(awk '/Unseal Key 2: (.*)/{print $4}' /vault/keys/secret)
UNSEAL_KEY3=$(awk '/Unseal Key 3: (.*)/{print $4}' /vault/keys/secret)
vault unseal $UNSEAL_KEY1
vault unseal $UNSEAL_KEY2
vault unseal $UNSEAL_KEY3
