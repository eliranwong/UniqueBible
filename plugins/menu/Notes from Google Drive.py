import subprocess, sys, os, config
from plugins.menu.NotesUtility.install import *
try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    modulesInstalled = True
except:
    modulesInstalled = False

def downloadNotes():
    try:
        upload = subprocess.Popen("{0} {1} download".format(sys.executable, os.path.join("plugins", "menu", "NotesUtility", "access_google_drive.py")), shell=True)
        *_, stderr = upload.communicate()
        if not stderr:
            config.mainWindow.displayMessage("Restored!")
            config.mainWindow.reloadCurrentRecord()
        else:
            config.mainWindow.displayMessage("Failed to download bible notes!")
    except:
        config.mainWindow.displayMessage("Failed to download bible notes!")

credentials = os.path.join("credentials.json")
noteFileCloudId = os.path.join("plugins", "menu", "NotesUtility", "noteFileGoogleCloudId.txt")
if not os.path.isfile(credentials):
    config.mainWindow.displayMessage("You have not yet enabled Goolge Drive API! \nRead for more information at: https://github.com/eliranwong/UniqueBible/wiki/Notes-Backup-with-Google-Drive")
    config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/Notes-Backup-with-Google-Drive")
elif not os.path.isfile(noteFileCloudId):
    config.mainWindow.displayMessage("You do not have a backup in Google Drive yet!")
else:
    if not modulesInstalled:
        print("Installing missing modules ...")
        installGoogleDriveModules()
        downloadNotes()
    else:
        downloadNotes()
