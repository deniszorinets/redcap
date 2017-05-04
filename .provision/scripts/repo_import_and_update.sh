#!/usr/bin/env bash
apt-get update -y
apt-get install -y software-properties-common python-software-properties
add-apt-repository ppa:fkrull/deadsnakes
echo deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main > /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
apt-get update -y
