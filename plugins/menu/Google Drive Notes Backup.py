import subprocess, sys, os, config
from plugins.menu.NotesUtility.install import *
try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    modulesInstalled = True
except:
    modulesInstalled = False

def uploadNotes():
    try:
        noteFileCloudId = os.path.join("plugins", "menu", "NotesUtility", "noteFileGoogleCloudId.txt")
        upload = subprocess.Popen("{0} {1} upload {2}".format(sys.executable, os.path.join("plugins", "menu", "NotesUtility", "access_google_drive.py"), config.marvelData), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = upload.communicate()
        if not stderr:
            text = stdout.decode("utf-8")
            if text.startswith("Please visit this URL"):
                text = "{0}\n".format(text.split("\n")[1])
            with open(noteFileCloudId, "w") as f:
                f.write(text)
            config.mainWindow.displayMessage("Uploaded 'note.sqlite' to Google Drive!\nFile ID: {0}".format(text[:-1]))
        else:
            print(stderr)
            config.mainWindow.displayMessage("Failed to upload bible notes!")
    except Exception as ex:
        print(ex)
        config.mainWindow.displayMessage("Failed to upload bible notes!")


credentials = os.path.join("credentials.json")
#noteFile = os.path.join(os.getcwd(), "marvelData", "note.sqlite")
noteFile = os.path.join(os.getcwd(), "marvelData", "note.sqlite") if config.marvelData == "marvelData" else os.path.join(config.marvelData, "note.sqlite")
if not os.path.isfile(credentials):
    config.mainWindow.displayMessage("You have not yet enabled Goolge Drive API! \nRead for more information at: https://github.com/eliranwong/UniqueBible/wiki/Notes-Backup-with-Google-Drive")
    config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/Notes-Backup-with-Google-Drive")
elif not os.path.isfile(noteFile):
    config.mainWindow.displayMessage("You have not created a bible note yet!")
else:
    if not modulesInstalled:
        print("Installing missing modules ...")
        installGoogleDriveModules()
        uploadNotes()
    else:
        uploadNotes()
