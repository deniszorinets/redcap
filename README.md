# RedCap IT Automation Tool
Simple, lightweight, flexible and secure tool for it automation

Based on Django

# REQUIREMENTS
- HashiCorp vault
- rabbitmq
- celery 4+
- postgresql 9.5+
- python 3.5+
- pip

# DEVELOPMENT INSTALLATION
- clone this repo
```git clone git@github.com:berylTechnologies/redcap.git```
- install vagrant
- use vagrant 
```vagrant up```
This will create fully prepared machine with development environment.
- use ```vagrant ssh``` - to pass to machine's terminal
- ```cd /vagrant_data/``` - here you will find redcap
- activate virtual environment ```source .env/bin/acivate```
- create admin user ```python manage.py createsuperuser```
- start celery ```celery -A redcap worker -l INFO```
- start redcap ```python manage.py runserver 0.0.0.0:8000```
- in your browser go to ```http://your_vagrant_ip:8000``` - here you will see swagger page with api commands
- admin panel located on ```http://your_vagrant_ip:8000/admin```

# DOCKER INSTALLATION 
- Install docker and docker-compose on your machine
- clone this repo
```git clone https://github.com/deniszorinets/redcap.git```
- go to Docker directory
```cd your_path/redcap/.docker```
- set passwords and logins in ```docker-compose.yml```
- build project
```docker-compose buid```
- start containers 
```docker-compose up -d```
- you can list working containers via: ```docker ps```. Your containers:
```
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                                    NAMES
a50ebbbe039d        docker_nginx        "nginx -g 'daemon ..."   37 minutes ago      Up 37 minutes       0.0.0.0:8080->8080/tcp, 80/tcp, 0.0.0.0:8443->8443/tcp   nginx
817fcbf52595        docker_redcap       "/bin/sh -c 'super..."   37 minutes ago      Up 37 minutes       0.0.0.0:8000->8000/tcp                                   redcap
b94ee187af4d        docker_vault        "docker-entrypoint..."   37 minutes ago      Up 36 minutes       0.0.0.0:8200->8200/tcp                                   vault
d700cc844c48        docker_db           "docker-entrypoint..."   37 minutes ago      Up 37 minutes       0.0.0.0:5432->5432/tcp                                   postgres
1ecc663e0bf4        rabbitmq:alpine     "docker-entrypoint..."   37 minutes ago      Up 37 minutes       4369/tcp, 5671/tcp, 25672/tcp, 0.0.0.0:5672->5672/tcp    rabbit
```
- NOTE! If one of containers doesn`t start, run containers again: ```docker-compose up -d```
- init vault
```docker exec -it vault sh -c "vault init >> /vault/keys/secret && cat /vault/keys/secret"```
- NOTE! Then programm show your unseal keys and vault tokken, like this:
```
Unseal Key 1: some key
Unseal Key 2: some key
Unseal Key 3: some key
Unseal Key 4: some key
Unseal Key 5: some key
Initial Root Token: tokken

Vault initialized with 5 keys and a key threshold of 3. Please
securely distribute the above keys. When the vault is re-sealed,
restarted, or stopped, you must provide at least 3 of these keys
to unseal it again.

Vault does not store the master key. Without at least 3 keys,
your vault will remain permanently sealed.
```
- Save tokken and keys!!!

- create config for redcap ```cd your_path/redcap/redcap/settings``` ```cp local.py.dist local.py``` edit local.py as you need. For example:
```
from .settings import *

DEBUG = False

VAULT_TOKEN = 'your_vault_token' <--- change to your vault token
VAULT_URL = 'http://vault:8200'

CELERY_BROKER_URL = 'amqp://RABBITMQ_DEFAULT_USER:RABBITMQ_DEFAULT_PASS@rabbit:5672//' <--- change USER and PASS

# If you want to receive notifications to your application - use following section. 
# RedCap will send POST request to this url with id of task and status
CUSTOM_CALLBACK = 'http://custom_callback_url'

# If you want to receive notifications to slack - create slack app and use following section
SLACK_URL = 'slack_url'
SLACK_USERNAME = 'RedCap'
SLACK_CHANNEL = '#redcap'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'redcap', <--- change this  
        'USER': 'redcap', <--- change this
        'PASSWORD': 'your_secret_pass', <--- change this
        'HOST': 'db',
        'PORT': '5432',
    }
}

```
- go to Docker directory
```cd your_path/redcap/.docker```
- run migrations
```docker exec -it redcap sh -c "cd redcap && python manage.py migrate"```
- create superuser (use this username and pass for website login)
```docker exec -it redcap sh -c "cd redcap && python manage.py createsuperuser"``` 
- collect static files
```docker exec -it redcap sh -c "cd redcap && python manage.py collectstatic"```
- restart app
```docker exec -t redcap sh -c "supervisorctl restart celery && supervisorctl restart gunicorn```
- after all on your ```localhost:8080``` you find swagger page. ```localhost:8080/admin``` admin page
- NOTE! You can change domain name in ```nginx/config/default.conf``` 


# PRODUCTION INSTALLATION (basic CentOS 7 example)
- update system:
```yum update```
- create directory for app:
```mkdir /opt/redcap```
- create application user:
```adduser redcap -d /opt/redcap -s /bin/false```
- grant permissions to directory:
```chown -R redcap:redcap /opt/redcap```
- ```cd /opt/redcap```
- install git:
```yum install git```
- clone this repo:
```git clone https://github.com/berylTechnologies/redcap.git```
- install required software:
    - add epel repo: ```yum install epel-release```
    - add ius repo: ```yum install -y https://centos7.iuscommunity.org/ius-release.rpm```
    - add nginx repo:
        ```
        [nginx]
        name=nginx repo
        baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
        gpgcheck=0
        enabled=1
        ```
        to ```/etc/yum.repos.d/nginx.repo```
    - add postgresql repo:
        ```
        yum install http://yum.postgresql.org/9.5/redhat/rhel-7-x86_64/pgdg-redhat95-9.5-2.noarch.rpm
        ```
    - install software:
        ```
        yum install postgresql95-server postgresql95-contrib postgresql95-devel \
        nginx rabbitmq-server python35u python35u-devel python35u-libs unzip gcc openssl-devel policycoreutils
        ```
    - install pip:
        ```
        curl -O https://bootstrap.pypa.io/get-pip.py
        python3.5 get-pip.py
        rm get-pip.py
        ```
    - install virtualenv:
        ```pip install virtualenv```
    - install hasicorp vault:
        - Download
            ```
            curl -O https://releases.hashicorp.com/vault/0.7.0/vault_0.7.0_linux_amd64.zip
            ```
        - unzip and install
            ```
            unzip vault_0.7.0_linux_amd64.zip
            mkdir -p /opt/vault/bin
            mv ./vault /opt/vault/bin
            echo "export PATH=\$PATH:/opt/vault/bin" > /etc/profile.d/vault.sh
            export PATH=$PATH:/opt/vault/bin
            rm vault_0.7.0_linux_amd64.zip
            ```
            
- configure software
    - configure postgresql
       - start postgresql server
       ```
       /usr/pgsql-9.5/bin/postgresql95-setup initdb
       systemctl enable postgresql-9.5.service
       systemctl start postgresql-9.5.service
       ```
       
       - edit ```/var/lib/pgsql/9.5/data/pg_hba.conf```
       and make configuration like following:
       ```
        # TYPE  DATABASE        USER            ADDRESS                 METHOD
        # "local" is for Unix domain socket connections only
        local   all             all                                     peer
        # IPv4 local connections:
        host    all             all             127.0.0.1/32            md5
        # IPv6 local connections:
        host    all             all             ::1/128                 md5
       ```
       - restart postgresql server
       ```systemctl restart postgresql-9.5```
       - create environment variable
            ```
            echo "export PATH=\$PATH:/usr/pgsql-9.5/bin/" > /etc/profile.d/postgresql.sh
            export PATH=$PATH:/usr/pgsql-9.5/bin/
            ```
    - start rabbitmq-server
        ```
        systemctl enable rabbitmq-server
        systemctl start rabbitmq-server
        ```
    - configure vault:
    
        *here will be example for simple configuration with __postgresql__ backend and __no TLS__ encryption. 
        It is higly recommended to use TLS and storage backend, that supports high availability(like Consul).
        More information you can find in [official documentation](https://www.vaultproject.io/docs/configuration/index.html)*
        + create vault user
            ```
            adduser vault -d /opt/vault/ -s /bin/false
            ```
        + create vault database user
            ```
            sudo -u postgres psql -x -c "CREATE USER vault WITH LOGIN PASSWORD 'your_secret_password'"
            ```
        + create vault database
            ```
            sudo -u postgres psql -x -c "CREATE DATABASE vault OWNER vault"
            ```
        + connect to database ```psql -U vault -W vault -h 127.0.0.1``` and execute sql under __vault__ user
            ```
            CREATE TABLE vault_kv_store (
              parent_path TEXT COLLATE "C" NOT NULL,
              path        TEXT COLLATE "C",
              key         TEXT COLLATE "C",
              value       BYTEA,
              CONSTRAINT pkey PRIMARY KEY (path, key)
            );
            
            CREATE INDEX parent_path_idx ON vault_kv_store (parent_path);
            ```
        + create config for vault server
            ```
            storage "postgresql" {
                connection_url = "postgres://vault:your_secret_password@localhost:5432/vault?sslmode=disable"
            }
    
            listener "tcp" {
                address     = "127.0.0.1:8200"
                tls_disable = 1
            }
            
            # need if running vault not under root
            disable_mlock = 1
            ```
        
            as ``/opt/vault/config.hcl``
        
        + create environment variable
            ```
            echo "export VAULT_ADDR=http://127.0.0.1:8200" >> /etc/profile.d/vault.sh
            export VAULT_ADDR=http://127.0.0.1:8200
            ```
        + create systemd unit for vault
            ```
            [Unit]
            Description=HasiCorp Vault Server
            After=network.target
            
            [Service]
            Type=simple
            User=vault
            Group=vault
            ExecStart=/opt/vault/bin/vault server -config=/opt/vault/config.hcl
            ExecStop=/bin/kill -TERM ${MAINPID}
            ExecReload=/bin/kill -HUP ${MAINPID}
            
            [Install]
            WantedBy=multi-user.target
            ```
            as ```/usr/lib/systemd/system/vault.service```
        + start vault server
            ```
            systemctl daemon-reload
            systemctl enable vault
            systemctl start vault
            ```
        + init vault
            ```
            vault init
            ```
            this command outputs Initial Root Token and Unseal Keys - save them or remember :)
        + unseal vault
        
            *By default vault storage is sealed - you cannot operate with it. 
            To unseal it you need to enter unseal keys. 
            You need to unseal it after every vault server restart*
            
            ```
            vault unseal your_first_unseal_key
            vault unseal your_second_unseal_key
            vault unseal your_third_unseal_key
            ```
    - configure redcap
        + create redcap database user
           ```
           sudo -u postgres psql -x -c "CREATE USER redcap WITH LOGIN PASSWORD 'your_secret_password'"
           ```
       + create database for redcap
           ```
           sudo -u postgres psql -x -c "CREATE DATABASE redcap OWNER redcap"
           ```
       + create virtual environment
            ```
            cd /opt/redcap
            virtualenv .env
            source .env/bin/activate
            ```
       + install python requirements
            ```
            cd /opt/redcap/redcap
            pip install -r requirements.txt
            ```
            on this stage you can get error message "Failed cleaning build dir for cryptography" - ignore it
    - configure gunicorn
        + create user
            ```adduser -M -s /bin/false redcap_gunicorn```
        + create systemd unit
            ```
            [Unit]
            Description=RedCap HTTPD
            After=network.target
            
            [Service]
            Type=simple
            User=redcap_gunicorn
            Group=redcap_gunicorn
            ExecStart=/opt/redcap/.env/bin/gunicorn -w 2 -k gevent --chdir /opt/redcap/redcap/ redcap.wsgi
            ExecStop=/bin/kill -TERM ${MAINPID}
            ExecReload=/bin/kill -HUP ${MAINPID}
            
            [Install]
            WantedBy=multi-user.target
            ```
            as ```/usr/lib/systemd/system/redcap-http.service```
        + reload daemons
            ```systemctl daemon-reload```
    - configure celery
        + create user
            ```adduser -M -s /bin/false redcap_celery```
        + create rabbitmq user
            ```
            rabbitmqctl add_user redcap_celery your_secret_password
            rabbitmqctl add_vhost redcap_celery
            rabbitmqctl set_user_tags redcap_celery celery
            rabbitmqctl set_permissions -p redcap_celery redcap_celery ".*" ".*" ".*"
            ```
        + create systemd unit
            ```
            [Unit]
            Description=RedCap Celery
            After=network.target
            
            [Service]
            Type=simple
            User=redcap_celery
            Group=redcap_celery
            WorkingDirectory=/opt/redcap/redcap
            ExecStart=/opt/redcap/.env/bin/celery -A redcap worker -l INFO
            ExecStop=/bin/kill -TERM ${MAINPID}
            ExecReload=/bin/kill -HUP ${MAINPID}
            
            [Install]
            WantedBy=multi-user.target
            ```
            as ```/usr/lib/systemd/system/redcap-celery.service```
        + reload daemons
            ```systemctl daemon-reload```
    - create config for redcap
        ```cd /opt/redcap/redcap/redcap/settings```
        ```cp local.py.dist local.py```
        edit local.py as you need. For example:
        ```
        from .settings import *

        DEBUG = False
        
        VAULT_TOKEN = 'your_vault_token'
        VAULT_URL = 'http://127.0.0.1:8200'
        
        CELERY_BROKER_URL = 'amqp://celery:rabbitmq_celery_user_pass@localhost:5672/rabbitmq_celery_vhost'
        
        # If you want to receive notifications to your application - use following section. 
        # RedCap will send POST request to this url with id of task and status
        CUSTOM_CALLBACK = 'http://custom_callback_url'
        
        # If you want to receive notifications to slack - create slack app and use following section
        SLACK_URL = 'slack_url'
        SLACK_USERNAME = 'RedCap'
        SLACK_CHANNEL = '#redcap'
        
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'redcap',
                'USER': 'redcap',
                'PASSWORD': 'your_secret_pass',
                'HOST': '127.0.0.1',
                'PORT': '5432',
            }
        }
        ```
    - run migrations
        ```
        cd /opt/redcap/redcap
        python manage.py migrate
        ```
    - create admin user
        ```
        python manage.py createsuperuser
        ```
    - collect static files
        ```
        python manage.py collectstatic
        ```
    - start application
        ```
        systemctl start redcap-http
        systemctl start redcap-celery
        systemctl enable redcap-http
        systemctl enable redcap-celery
        ```
        
- configure nginx
    - start nginx
        ```
        systemctl start nginx
        systemctl enable nginx
        ```
    - create virtualhost for redcap
        ```
        server {
          listen 80;
          server_name  example.com;
        
          location = /favicon.ico { access_log off; log_not_found off; }
          location /static/ {
                alias /opt/redcap/redcap/redcap/static/;
          }
        
        
          location / {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_pass http://127.0.0.1:8000;
            }
        
        }
        ```
    - it is strongly recommended to use tls. For example with letsencrypt:
        ```
        server {
            listen 80;
            server_name example.com;
        
        
            location /.well-known/acme-challenge {
                root /var/www/letsencrypt;
            }
        
            location / {
               return 301 https://example.com$request_uri;
            }
        }
        
        server {
          listen 443 ssl;
          server_name example.com;
          server_tokens off;
        
          access_log  /var/log/nginx/example.com.access.log;
          error_log   /var/log/nginx/example.com.error.log;
           
          ssl_certificate /usr/local/etc/letsencrypt/live/example.com/fullchain.pem;
          ssl_certificate_key /usr/local/etc/letsencrypt/live/example.com/privkey.pem; 
        
          ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
          ssl_prefer_server_ciphers on;
          ssl_dhparam /etc/ssl/certs/dhparam.pem;
          ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
          ssl_session_timeout 1d;
          ssl_session_cache shared:SSL:50m;
          ssl_stapling on;
          ssl_stapling_verify on;
          add_header Strict-Transport-Security max-age=15768000; 
          
          location = /favicon.ico { access_log off; log_not_found off; }
          location /static/ {
                alias /opt/redcap/redcap/redcap/static/;
          }
        
          location / {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_pass http://127.0.0.1:8000;
            }
        }
        ```
    - add selinux rule for nginx to use reverse proxy
    ```setsebool -P httpd_can_network_connect 1```
    - reload nginx
    ```nginx -s reload```

# PRODUCTION INSTALLATION (basic Ubuntu 17.04 example)
- update system:
    ```
    sudo apt update
    sudo apt upgrade
    ```
- create directory for app:
```sudo mkdir /opt/redcap```
- create application user:
```sudo adduser redcap --home /opt/redcap --shell /bin/false --disabled-login --disabled-password```
- grant permissions to directory:
```sudo chown -R redcap:redcap /opt/redcap```
- ```cd /opt/redcap```
- install git:
```sudo apt install git```
- clone this repo:
```sudo git clone https://github.com/berylTechnologies/redcap.git```
- install required software:
    - install software:
        ```
        sudo apt install python3.6 python3.6-dev postgresql-9.6 postgresql-client-9.6 postgresql-contrib-9.6 \
        postgresql-server-dev-9.6 libssl1.0-dev gcc unzip rabbitmq-server nginx
        ```
    - install pip:
        ```
        sudo curl -O https://bootstrap.pypa.io/get-pip.py
        sudo python3.6 get-pip.py
        sudo rm get-pip.py
        ```
    - install virtualenv:
        ```sudo pip install virtualenv```
    - install hasicorp vault:
        - Download
            ```
            sudo curl -O https://releases.hashicorp.com/vault/0.7.0/vault_0.7.0_linux_amd64.zip
            ```
        - unzip and install
            ```
            sudo unzip vault_0.7.0_linux_amd64.zip
            sudo mkdir -p /opt/vault/bin
            sudo mv ./vault /opt/vault/bin
            echo "export PATH=\$PATH:/opt/vault/bin" | sudo tee --append /etc/profile.d/vault.sh
            export PATH=$PATH:/opt/vault/bin
            sudo rm vault_0.7.0_linux_amd64.zip
            ```
            
- configure software
    - configure vault:
    
        *here will be example for simple configuration with __postgresql__ backend and __no TLS__ encryption. 
        It is higly recommended to use TLS and storage backend, that supports high availability(like Consul).
        More information you can find in [official documentation](https://www.vaultproject.io/docs/configuration/index.html)*
        + create vault user
            ```
            sudo adduser vault --home /opt/vault/ --shell /bin/false --disabled-login --disabled-password
            ```
        + create vault database user
            ```
            sudo -u postgres psql -x -c "CREATE USER vault WITH LOGIN PASSWORD 'your_secret_password'"
            ```
        + create vault database
            ```
            sudo -u postgres psql -x -c "CREATE DATABASE vault OWNER vault"
            ```
        + connect to database ```psql -U vault -W vault -h 127.0.0.1``` and execute sql under __vault__ user
            ```
            CREATE TABLE vault_kv_store (
              parent_path TEXT COLLATE "C" NOT NULL,
              path        TEXT COLLATE "C",
              key         TEXT COLLATE "C",
              value       BYTEA,
              CONSTRAINT pkey PRIMARY KEY (path, key)
            );
            
            CREATE INDEX parent_path_idx ON vault_kv_store (parent_path);
            ```
        + create config for vault server
            ```
            storage "postgresql" {
                connection_url = "postgres://vault:your_secret_password@localhost:5432/vault?sslmode=disable"
            }
    
            listener "tcp" {
                address     = "127.0.0.1:8200"
                tls_disable = 1
            }
            
            # need if running vault not under root
            disable_mlock = 1
            ```
        
            as ``/opt/vault/config.hcl``
        
        + create environment variable
            ```
            echo "export VAULT_ADDR=http://127.0.0.1:8200" | sudo tee --append /etc/profile.d/vault.sh
            export VAULT_ADDR=http://127.0.0.1:8200
            ```
        + create systemd unit for vault
            ```
            [Unit]
            Description=HasiCorp Vault Server
            After=network.target
            
            [Service]
            Type=simple
            User=vault
            Group=vault
            ExecStart=/opt/vault/bin/vault server -config=/opt/vault/config.hcl
            ExecStop=/bin/kill -TERM ${MAINPID}
            ExecReload=/bin/kill -HUP ${MAINPID}
            
            [Install]
            WantedBy=multi-user.target
            ```
            as ```/etc/systemd/system/vault.service```
        + start vault server
            ```
            sudo systemctl daemon-reload
            sudo systemctl enable vault
            sudo systemctl start vault
            ```
        + init vault
            ```
            vault init
            ```
            this command outputs Initial Root Token and Unseal Keys - save them or remember :)
        + unseal vault
        
            *By default vault storage is sealed - you cannot operate with it. 
            To unseal it you need to enter unseal keys. 
            You need to unseal it after every vault server restart*
            
            ```
            vault unseal your_first_unseal_key
            vault unseal your_second_unseal_key
            vault unseal your_third_unseal_key
            ```
    - configure redcap
        + create redcap database user
           ```
           sudo -u postgres psql -x -c "CREATE USER redcap WITH LOGIN PASSWORD 'your_secret_password'"
           ```
       + create database for redcap
           ```
           sudo -u postgres psql -x -c "CREATE DATABASE redcap OWNER redcap"
           ```
       + create virtual environment under root
            ```
            sudo su
            cd /opt/redcap
            virtualenv .env
            source .env/bin/activate
            ```
       + install python requirements
            ```
            cd /opt/redcap/redcap
            pip install -r requirements.txt
            ```
            on this stage you can get error message "Failed cleaning build dir for cryptography" - ignore it
    - configure gunicorn
        + create user
            ```sudo adduser redcap_gunicorn --no-create-home --shell /bin/false --disabled-login --disabled-password```
        + create systemd unit
            ```
            [Unit]
            Description=RedCap HTTPD
            After=network.target
            
            [Service]
            Type=simple
            User=redcap_gunicorn
            Group=redcap_gunicorn
            ExecStart=/opt/redcap/.env/bin/gunicorn -w 2 -k gevent --chdir /opt/redcap/redcap/ redcap.wsgi
            ExecStop=/bin/kill -TERM ${MAINPID}
            ExecReload=/bin/kill -HUP ${MAINPID}
            
            [Install]
            WantedBy=multi-user.target
            ```
            as ```/etc/systemd/system/redcap-http.service```
        + reload daemons
            ```sudo systemctl daemon-reload```
    - configure celery
        + create user
            ```sudo adduser redcap_celery --no-create-home --shell /bin/false --disabled-login --disabled-password```
        + create rabbitmq user
            ```
            sudo rabbitmqctl add_user redcap_celery your_secret_password
            sudo rabbitmqctl add_vhost redcap_celery
            sudo rabbitmqctl set_user_tags redcap_celery celery
            sudo rabbitmqctl set_permissions -p redcap_celery redcap_celery ".*" ".*" ".*"
            ```
        + create systemd unit
            ```
            [Unit]
            Description=RedCap Celery
            After=network.target
            
            [Service]
            Type=simple
            User=redcap_celery
            Group=redcap_celery
            WorkingDirectory=/opt/redcap/redcap
            ExecStart=/opt/redcap/.env/bin/celery -A redcap worker -l INFO
            ExecStop=/bin/kill -TERM ${MAINPID}
            ExecReload=/bin/kill -HUP ${MAINPID}
            
            [Install]
            WantedBy=multi-user.target
            ```
            as ```/etc/systemd/system/redcap-celery.service```
        + reload daemons
            ```sudo systemctl daemon-reload```
    - create config for redcap
        ```cd /opt/redcap/redcap/redcap/settings```
        ```sudo cp local.py.dist local.py```
        edit local.py as you need. For example:
        ```
        from .settings import *

        DEBUG = False
        
        VAULT_TOKEN = 'your_vault_token'
        VAULT_URL = 'http://127.0.0.1:8200'
        
        CELERY_BROKER_URL = 'amqp://celery:rabbitmq_celery_user_pass@localhost:5672/rabbitmq_celery_vhost'
        
        # If you want to receive notifications to your application - use following section. 
        # RedCap will send POST request to this url with id of task and status
        CUSTOM_CALLBACK = 'http://custom_callback_url'
        
        # If you want to receive notifications to slack - create slack app and use following section
        SLACK_URL = 'slack_url'
        SLACK_USERNAME = 'RedCap'
        SLACK_CHANNEL = '#redcap'
        
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'redcap',
                'USER': 'redcap',
                'PASSWORD': 'your_secret_pass',
                'HOST': '127.0.0.1',
                'PORT': '5432',
            }
        }
        ```
    - run migrations
        ```
        cd /opt/redcap/redcap
        python manage.py migrate
        ```
    - create admin user
        ```
        python manage.py createsuperuser
        ```
    - collect static files
        ```
        python manage.py collectstatic
        ```
    - start application
        ```
        systemctl start redcap-http
        systemctl start redcap-celery
        systemctl enable redcap-http
        systemctl enable redcap-celery
        ```
        
- configure nginx
    - create virtualhost for redcap
        ```
        server {
          listen 80;
          server_name  example.com;
        
          location = /favicon.ico { access_log off; log_not_found off; }
          location /static/ {
                alias /opt/redcap/redcap/redcap/static/;
          }
        
        
          location / {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_pass http://127.0.0.1:8000;
            }
        
        }
        ```
    - it is strongly recommended to use tls. For example with letsencrypt:
        ```
        server {
            listen 80;
            server_name example.com;
        
        
            location /.well-known/acme-challenge {
                root /var/www/letsencrypt;
            }
        
            location / {
               return 301 https://example.com$request_uri;
            }
        }
        
        server {
          listen 443 ssl;
          server_name example.com;
          server_tokens off;
        
          access_log  /var/log/nginx/example.com.access.log;
          error_log   /var/log/nginx/example.com.error.log;
           
          ssl_certificate /usr/local/etc/letsencrypt/live/example.com/fullchain.pem;
          ssl_certificate_key /usr/local/etc/letsencrypt/live/example.com/privkey.pem; 
        
          ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
          ssl_prefer_server_ciphers on;
          ssl_dhparam /etc/ssl/certs/dhparam.pem;
          ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
          ssl_session_timeout 1d;
          ssl_session_cache shared:SSL:50m;
          ssl_stapling on;
          ssl_stapling_verify on;
          add_header Strict-Transport-Security max-age=15768000; 
          
          location = /favicon.ico { access_log off; log_not_found off; }
          location /static/ {
                alias /opt/redcap/redcap/redcap/static/;
          }
        
          location / {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_pass http://127.0.0.1:8000;
            }
        }
        ```

    - reload nginx
    ```nginx -s reload```
    

**It is highly recommended to restrict access to redcap from public network and use strict firewall rules**
