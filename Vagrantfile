# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/precise64"


  config.vm.box_check_update = false

  # config.vm.network "forwarded_port", guest: 8080, host: 8080

  # config.vm.network "private_network", ip: "192.168.137.254"
  # config.vm.network "public_network"

  config.vm.synced_folder ".", "/vagrant_data", type: "smb"

  config.vm.provision "file", source: "./.provision/vault.conf", destination: "vault.conf"
  config.vm.provision "file", source: "./.provision/supervisord_vault.conf", destination: "supervisord_vault.conf"
  config.vm.provision "file", source: "./.provision/vault_db.sql", destination: "vault_db.sql"
  config.vm.provision "file", source: "./.provision/vault_tables.sql", destination: "vault_tables.sql"

  config.vm.provision "shell", inline: <<-SHELL
    cd /home/vagrant
    apt-get install -y software-properties-common python-software-properties
    add-apt-repository ppa:fkrull/deadsnakes

    echo deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main > /etc/apt/sources.list.d/pgdg.list
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

    apt-get update -y
    apt-get upgrade -y
    apt-get install -y python3.5 python3.5-dev postgresql-9.6 postgresql-client-9.6 postgresql-contrib-9.6 postgresql-server-dev-9.6 gcc make openssl libssl-dev unzip vim zsh htop supervisor rabbitmq-server

    wget -q https://bootstrap.pypa.io/get-pip.py > /dev/null
    wget -q https://releases.hashicorp.com/vault/0.6.5/vault_0.6.5_linux_amd64.zip > /dev/null

    unzip vault_0.6.5_linux_amd64.zip
    
    mkdir /etc/vault
    mv vault /usr/sbin/

    mv vault_db.sql /etc/vault
    mv vault_tables.sql /etc/vault
    mv vault.conf /etc/vault/server.conf
    mv supervisord_vault.conf /etc/supervisor/conf.d/vault.conf

    /etc/init.d/supervisor stop
    /etc/init.d/supervisor start

    su postgres -c "psql -f /etc/vault/vault_db.sql"

    export PGPASSWORD="vault"
    su postgres -c "psql -Uvault -h127.0.0.1 -d vault -f /etc/vault/vault_tables.sql"

    supervisorctl start vault
    sleep 5

    export VAULT_ADDR=http://127.0.0.1:8200 

    vault init >> /etc/vault/keys

    python3.5 get-pip.py
    pip install virtualenv

    rabbitmqctl add_user celery celery
    rabbitmqctl add_vhost celery
    rabbitmqctl set_user_tags celery celery
    rabbitmqctl set_permissions -p celery celery ".*" ".*" ".*"

    rm get-pip.py
    rm vault_0.6.5_linux_amd64.zip
    rm /etc/vault/vault_db.sql
    rm /etc/vault/vault_tables.sql

  SHELL
end
