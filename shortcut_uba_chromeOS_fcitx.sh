#!/bin/bash
export QT_QPA_PLATFORM=wayland
export QT_IM_MODULE=fcitx
/usr/bin/urxvt &
source $HOME/UniqueBible/venv/bin/activate
$HOME/UniqueBible/venv/bin/python3 /home/eliranwong/UniqueBible/main.py
