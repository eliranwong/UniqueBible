# Example: Install & Run on macOS / Linux

There are different ways to install.  Below is an example.

# 1. Download & Install a Python Distribution First

Go to https://www.python.org/downloads/

Download a version 3.6+

# 2. Download a copy of UniqueBible.app

Use the download button on this page to download a zip copy.<br>

<img src="screenshots/downloadButton.png">

The following steps assume that your downloaded file is located in "Downloads" of your home directory, i.e. ~/Downloads/.<br>

# 3. Open your Terminal

On Linux, open a terminal app

On mac, open "Applications > Utilities > Terminal.app"

# 4. Enter Commands

> cd ~<br>
> unzip ~/Downloads/UniqueBible-master.zip<br>
> cd UniqueBible-master<br>
> python3 -m venv venv<br>
> source venv/bin/activate<br>
> pip3 install PySide2<br>
> pip3 install PyPDF2 python-docx gdown diff_match_patch langdetect pygithub qt-material pypinyin opencc telnetlib3 ibm-watson babel

# 5. Run the app

if you keep the terminal open after step 3, enter:

> python3 main.py<br>

if you open a new session, enter:

> cd ~/UniqueBible-master<br>
> source venv/bin/activate<br>
> python3 main.py<br>

# 6. Create a Shortcut File for Double-clicking on macOS

There are different ways to create a shortcut, below is an example.

Create a plain text file, e.g. UniqueBible.sh, and place on your desktop.

Paste the following lines in the file and save changes:

> cd ~/UniqueBible-master<br>
> source venv/bin/activate<br>
> python3 main.py<br>

Open your terminal and enter:

> chmod +x ~/Desktop/UniqueBible.sh

On mac, right click the file UniqueBible.sh, select "Get Info".

<img src="screenshots/mac_shortcut1.png">

In the section "Open with:", select "Terminal.app" as default.

<img src="screenshots/mac_shortcut2.png">

Now, you can double-click the file "UniqueBible.sh" to run the app directly.

# 7. Create a Shortcut on Linux

Create a plain text file /usr/share/applications/UniqueBibleApp.desktop

For example, if you use nano,

> sudo nano /usr/share/applications/UniqueBibleApp.desktop

Paste the following content, but replace your_username with your usename on your device

> [Desktop Entry]<br>
> Version=1.0<br>
> Type=Application<br>
> Terminal=false<br>
> Path=/home/your_username/UniqueBible-master/<br>
> Exec=python3 /home/your_username/UniqueBible-master/main.py<br>
> Icon=/home/your_username/UniqueBible-master/htmlResources/UniqueBibleApp.png<br>
> Name=Unique Bible App<br>

Saves changes by pressing "Ctrl + O"

Exit nano by pressing "Ctrl + X"
