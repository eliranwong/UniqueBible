#!/bin/bash

# Specify the path of UniqueBible folder in the following line
ubaFolder="$HOME/UniqueBible/"

cd $ubaFolder
source venv/bin/activate
python3 main.py & disown

exit
