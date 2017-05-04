#!/usr/bin/env bash
cd /home/vagrant
wget -q https://nodejs.org/dist/v7.9.0/node-v7.9.0-linux-x64.tar.xz > /dev/null

tar -xvf node-v7.9.0-linux-x64.tar.xz

mv node-v7.9.0-linux-x64 /opt/nodejs

export PATH=$PATH:/opt/nodejs/bin/

echo "export PATH=\$PATH:/opt/nodejs/bin/" > /etc/profile.d/nodejs.sh