#!/bin/bash
export QT_QPA_PLATFORM=wayland
export QT_IM_MODULE=fcitx
/usr/bin/urxvt &
source /home/eliranwong/UniqueBible/venv/bin/activate
/home/eliranwong/UniqueBible/venv/bin/python3 /home/eliranwong/UniqueBible/main.py
