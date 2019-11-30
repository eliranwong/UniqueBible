#!/bin/bash
# Specify the path of UniqueBible folder in the following line
ubaFolder="$HOME/UniqueBible/"

# Connect to display server
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0

# To work better with mesa-utils
export -n LIBGL_ALWAYS_INDIRECT

# Set QStandardPaths
export XDG_RUNTIME_DIR=/tmp/runtime-$USER

# Input method [Optional]
# You may enable ibus or fcitx below.
# To use ibus or fcitx, you need to install them first.
# Adjust details to suit your own needs.
# Remarks: Do NOT use ibus and fcitx at the same time.

# Lanuch ibus service & set variables:
#dbus-launch ibus-daemon -x -d
#export LC_CTYPE=zh_CN.UTF-8
#export XIM=ibus
#export XIM_PROGRAM=/usr/bin/ibus
#export QT_IM_MODULE=ibus
#export GTK_IM_MODULE=ibus
#export XMODIFIERS=@im=ibus
#export DefaultIMModule=ibus

# Lanuch fcitx service & set variables:
#dbus-launch /usr/bin/fcitx-autostart > /dev/null 2>&1
#export LC_CTYPE=zh_CN.UTF-8
#export XIM=fcitx
#export XIM_PROGRAM=/usr/bin/fcitx
#export QT_IM_MODULE=fcitx
#export GTK_IM_MODULE=fcitx
#export XMODIFIERS=@im=fcitx
#export DefaultIMModule=fcitx

cd $ubaFolder
source venv/bin/activate
dbus-launch python3 main.py & disown

exit
