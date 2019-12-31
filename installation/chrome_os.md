# Details
Find details at https://github.com/eliranwong/UniqueBible/blob/master/README.md

Below is a tested example.

# Prerequisites:

Install pyhon3 and pip tools first:

> sudo apt install python3 python-setuptools python3-pip python3-venv

# Install dependencies<br>

Enter in terminal:

> pip3 install PyPDF2 python-docx gdown diff_match_patch

> pip3 install --index-url=https://download.qt.io/official_releases/QtForPython/ pyside2 --trusted-host download.qt.io

[Remarks: 
* "PySide2" folder, installed with the command above, is located at "~/.local/lib/python3.5/site-packages/PySide2"<br>
[instead of "/usr/local/lib/python3.5/dist-packages/PySide2"]<br>
* In our testings, command "pip3 install PySide2" encounters memory errors on some low-memory chromebooks.  The above command installs wheel directly from Qt servers with this command.  Find details at: https://wiki.qt.io/Qt_for_Python/GettingStarted
]<br>

# Download
Enter in terminal:

> cd ~<br>
> wget https://github.com/eliranwong/UniqueBible/archive/master.zip<br>
> unzip master.zip<br>

# Run
Enter in Linux terminal:

> cd ~/UniqueBible-master/ && python3 main.py<br>

# Create a Shortcut
Create a shortcut in chrome os application menu<br>
[so you don't need Linux terminal to run the app]

First, edit file "~/UniqueBible-master/shortcut_uba_Linux.desktop", by replacing username "eliranwong" with your username.<br>

Second, run the following command in Linux terminal:<br>

> sudo cp ~/UniqueBible-master/shortcut_uba_Linux.desktop /usr/share/applications/UniqueBibleApp.desktop<br>

Locate the created shortcut in folder "Linux apps" inside chrome os application menu.<br>

[To read more about .desktop file: https://developer.gnome.org/integration-guide/stable/desktop-files.html.en]

# Use Virtual Keyboard

You have an option to use virtual keyboards for typing.

Virtual keyboards are useful for touch-screen users.  It may also facilitate input of Hebrew, Greek or other non-English characters on systems, where non-English keyboards are not installed.

<img src="../screenshots/screenshot_virtualKeyboard.png">

To enable built-in virtual keyboards, edit file "config.py" with a text editor.

<b>ATTENTION:</b> Close UniqueBible.app first before you edit file "config.py".  Otherwise, your changes may be overwritten later by the app upon closing.  Re-open the app only after you edit and save the changes in "config.py".

Change the option "virtualKeyboard" FROM:

virtualKeyboard = False

TO:

virtualKeyboard = True

<b>Remarks:</b> You need to close the virtual keyboard before you can close the app.  You can use the button located at the right lower corner of the virtual keyboard to close it.

# Support fcitx [testing]

This following may work on some Linux distributions, but not on Linux distribution which comes with Chrome OS 78.

> cp /usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so ~/.local/lib/python3.5/site-packages/PySide2/Qt/plugins/platforminputcontexts/

> chmod +x ~/.local/lib/python3.5/site-packages/PySide2/Qt/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so
