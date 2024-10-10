#!/bin/bash

cd ~
wget "https://github.com/eliranwong/UniqueBible/archive/master.zip"
unzip master.zip
cd UniqueBible-master
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

