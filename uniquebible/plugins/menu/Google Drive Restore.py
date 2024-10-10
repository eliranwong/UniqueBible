import subprocess, sys, os
from uniquebible import config
try:
    from plugins.menu.GoogleDriveUtility.install import *
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    modulesInstalled = True
except:
    modulesInstalled = False

def downloadFiles():
    message = ""
    try:
        filesToBackupFile = os.path.join("plugins", "menu", "GoogleDriveUtility", "files_to_backup.txt")
        filesToBackupList = []
        if os.path.exists(filesToBackupFile):
            with open(filesToBackupFile) as input:
                filesToBackupList = [line.strip() for line in input.readlines()]
        for file in filesToBackupList:
            download = subprocess.Popen("{0} {1} download {2}".format(sys.executable, os.path.join("plugins", "menu", "GoogleDriveUtility", "access_google_drive.py"), file), shell=True)
            *_, stderr = download.communicate()
            if not stderr:
                message += f"Downloaded {file}\n"
            else:
                print(stderr)
                message += f"Could not download {file}\n"
    except Exception as ex:
        print(ex)
        message = "Failed to download: " + ex
    config.mainWindow.reloadCurrentRecord()
    config.mainWindow.displayMessage(message)

credentials = os.path.join("credentials.json")
if not os.path.isfile(credentials):
    config.mainWindow.displayMessage("You have not yet enabled Google Drive API! \nRead for more information at: https://github.com/eliranwong/UniqueBible/wiki/Backup-with-Google-Drive")
    config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/Backup-with-Google-Drive")
else:
    if not modulesInstalled:
        print("Installing missing modules ...")
        installGoogleDriveModules()
        downloadFiles()
    else:
        downloadFiles()
