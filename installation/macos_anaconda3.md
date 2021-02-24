# Example: Install & Run on macOS

There are different ways to install.  Below is an example.

# 1. Download & Install a Python Distribution First

For example, go to https://www.anaconda.com/distribution/#download-section and download a python version 3.7.

<img src="screenshots/mac_anaconda1.png">

Open the installer from "Downloads" or your "Downloads" folder.

<img src="screenshots/mac_anaconda2.png">

Follow through the installer to complete the installation.

<img src="screenshots/mac_anaconda3.png">

<b>Remarks:</b>

In this example, we use a Anaconda distribution.

For example on standard python distribution, please read https://github.com/eliranwong/UniqueBible/blob/master/installation/Readme.md

# 2. Open your Terminal

On Linux, open a terminal app

On mac, open "Applications > Utilities > Terminal.app"

# 3. Install Dependencies

Enter the following command in terminal, one by one:

> conda install -c conda-forge pyside2<br>
> conda install -c vladsaveliev gdown<br>
> conda install -c conda-forge pypdf2<br>
> conda install -c conda-forge python-docx<br>
> conda install -c conda-forge diff-match-patch<br>
> conda install -c conda-forge ibm-watson<br>
> conda install -c anaconda babel<br>
> conda install -c conda-forge langdetect<br>
> conda install -c conda-forge pygithub

<b>Remarks:</b>  When question "Proceed ([y]/n)?" comes up, simply enter "y".

# 4. Download a copy of UniqueBible.app

Use the download button on this page to download a zip copy.<br>

<img src="screenshots/downloadButton.png">

The downloaded zip file should be automatically "unzipped" on mac.

# 5. Move the Folder

You can place the folder "UniqueBible-master" anywhere you like on your mac.

In the following steps, we assume the folder is placed on your Desktop, i.e. ~/Desktop/UniqueBible-master

# 6. Run 

Enter the following commands in terminal:

> ~/Desktop/UniqueBible-master<br>
> python3 main.py

# 7. Create a Shortcut

There are different ways to create a shortcut, below is an example.

Create a plain text file, e.g. UniqueBible.sh, and place on your desktop.

Paste the following lines in the file and save changes:

> ~/Desktop/UniqueBible-master<br>
> python3 main.py

Open your terminal and enter:

> chmod +x ~/Desktop/UniqueBible.sh

On mac, right click the file UniqueBible.sh, select "Get Info".

<img src="screenshots/mac_shortcut1.png">

In the section "Open with:", select "Terminal.app" as default.

<img src="screenshots/mac_shortcut2.png">

Now, you can double-click the file "UniqueBible.sh" to run the app directly.
