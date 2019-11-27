# Example: Install & Run on macOS / Linux

There are different ways to install.  Below is an example.

# 1. Download & Install a Python Distribution First

Go to https://www.python.org/downloads/

Download a version 3.

We recommend to download a 3.7.x version, e.g. 3.7.5.  We haven't tested our app with the latest python distribution 3.8.

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
> pip3 install PyPDF2<br>
> pip3 install python-docx<br>
> pip3 install gdown<br>

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

On mac, right click the file UniqueBible.sh, select "Terminal" as the application to "Open With".

# 7. Create a Shortcut on Linux

