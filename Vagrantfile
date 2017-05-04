# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/precise64"
  config.vm.box_check_update = false
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  config.vm.provider "hyperv" do |hv, override|
   override.vm.synced_folder ".", "/vagrant_data",
     type:  "smb",
     owner: "vagrant",
     group: "vagrant",
     mount_options: ["mfsymlinks,dir_mode=0775,file_mode=0775"]
   hv.differencing_disk = true
  end

  config.vm.provider "virtualbox" do |vb, override|
   override.vm.synced_folder ".", "/vagrant_data",
     owner: "vagrant",
     group: "vagrant",
     mount_options: ["dmode=775,fmode=775"]
  end

  config.vm.provision "file", source: "./.provision/files/vault.conf", destination: "vault.conf"
  config.vm.provision "file", source: "./.provision/files/supervisord_vault.conf", destination: "supervisord_vault.conf"
  config.vm.provision "file", source: "./.provision/files/vault_db.sql", destination: "vault_db.sql"
  config.vm.provision "file", source: "./.provision/files/vault_tables.sql", destination: "vault_tables.sql"

  config.vm.provision "shell", path: "./.provision/scripts/repo_import_and_update.sh"
  config.vm.provision "shell", path: "./.provision/scripts/install_software_from_repo.sh"
  config.vm.provision "shell", path: "./.provision/scripts/install_vault.sh"
  config.vm.provision "shell", path: "./.provision/scripts/pip_install.sh"
  config.vm.provision "shell", path: "./.provision/scripts/install_nodejs.sh"
  config.vm.provision "shell", path: "./.provision/scripts/rabbitmq_config.sh"
  config.vm.provision "shell", path: "./.provision/scripts/proj_setup.sh"
  config.vm.provision "shell", path: "./.provision/scripts/cleanup.sh"
  config.vm.provision "shell", path: "./.provision/scripts/vault_unseal.sh", run: "always"

end