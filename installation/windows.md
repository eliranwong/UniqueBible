
# Install Chocolatey

Chocolatey is the package manager for Windows (like apt-get but for Windows)

For details on installing Chocolatey, please read: https://chocolatey.org/install.  The command in step 3 below is copied from the official website at the time of writting.

1) Right-click Windows Icon, located at left lower corner

2) Select and open "Windows PowerShell (Admin)"

3) Enter the following command:

> Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Python & Git

1) Right-click Windows Icon, located at left lower corner

2) Select and open "Windows PowerShell (Admin)"

3) Enter the following commands:

> choco install python

> choco install git

# Download & Setup UniqueBible.app

1) Right-click Windows Icon, located at left lower corner

2) Select and open "Windows PowerShell"<br>
<b>[Remarks: Please note that in the following steps, use "Windows PowerShell" instead of "Windows PowerShell (Admin)"]</b>

3) Enter the following command:

> cd .\Documents\

> git clone https://github.com/eliranwong/UniqueBible

> cd .\UniqueBible\

> python -m venv venv

> .\venv\Scripts\activate

> pip3 install gdown PySide2 PyPDF2 python-docx diff_match_patch

# Run UniqueBible.app

> python .\main.py

Alternatively, double-click the file "shortcut_uba_Windows.bat" in the UniqueBible folder.

# Create a Desktop Shortcut

1) Right click the file "shortcut_uba_Windows.bat" in the UniqueBible folder.

2) Select "Send to > Desktop (create shortcut)"

3) Rename the desktop shortcut "shortcut_uba_Windows.bat - Shortcut" to "UniqueBible.app"

4) Right-click the shortcut file and select "Properties"

5) Change Icon..., browse and select "theText.ico" in folder "UniqueBible\htmlResources", i.e.:

%USERPROFILE%\Documents\UniqueBible\htmlResources\theText.ico

# Run with Desktop Shortcut

Double-click the created shortcut file
