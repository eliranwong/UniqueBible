#!/bin/bash
cd $HOME/UniqueBible
source venv/bin/activate
/usr/bin/env QT_QPA_PLATFORM=xcb QT_LOGGING_RULES=*=false python3 main.py
