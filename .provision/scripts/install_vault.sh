#!/usr/bin/env bash
cd /home/vagrant
wget -q https://releases.hashicorp.com/vault/0.6.5/vault_0.6.5_linux_amd64.zip > /dev/null

unzip vault_0.6.5_linux_amd64.zip

mkdir /etc/vault
mv vault /usr/sbin/

mv vault_db.sql /etc/vault
mv vault_tables.sql /etc/vault
mv vault.conf /etc/vault/server.conf

mv supervisord_vault.conf /etc/supervisor/conf.d/vault.conf
/etc/init.d/supervisor stop

su postgres -c "psql -f /etc/vault/vault_db.sql"
export PGPASSWORD="vault"
su postgres -c "psql -Uvault -h127.0.0.1 -d vault -f /etc/vault/vault_tables.sql"

/etc/init.d/supervisor start
sleep 5

export VAULT_ADDR=http://127.0.0.1:8200

vault init >> /etc/vault/keys