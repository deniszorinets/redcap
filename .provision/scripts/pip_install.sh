#!/usr/bin/env bash
cd /home/vagrant
wget -q https://bootstrap.pypa.io/get-pip.py > /dev/null
python3.5 get-pip.py
pip install virtualenv