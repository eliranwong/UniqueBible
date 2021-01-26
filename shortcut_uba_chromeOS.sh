#!/bin/bash
export QT_QPA_PLATFORM=wayland
cd $HOME/UniqueBible
source venv/bin/activate
python3 main.py
