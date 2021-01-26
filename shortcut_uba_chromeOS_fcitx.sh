#!/bin/bash
export QT_QPA_PLATFORM=wayland
export QT_IM_MODULE=fcitx
cd $HOME/UniqueBible
source venv/bin/activate
python3 main.py
