#!/usr/bin/env bash
sudo -u postgres psql -x -c "CREATE USER redcap WITH LOGIN PASSWORD 'redcap'"
sudo -u postgres psql -x -c "CREATE DATABASE redcap OWNER redcap"

cd /vagrant_data

VAULT_ROOT_TOKEN=$(awk '/Initial Root Token: (.*)/{print $4}' /etc/vault/keys)

cp redcap/settings/local.py.dist redcap/settings/local.py

echo "VAULT_TOKEN='$VAULT_ROOT_TOKEN'" >> redcap/settings/local.py

virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
python manage.py migrate

cd redcap/webapp

npm install
npm install -g gulp

gulp makejs
gulp makecss
