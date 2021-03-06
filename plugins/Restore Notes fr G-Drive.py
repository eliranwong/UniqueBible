import subprocess, sys, os, config
try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    modulesInstalled = True
except:
    modulesInstalled = False

def installGoogleDriveModules():
    try:
        # Automatic setup does not start on some device because pip tool is too old
        updatePip = subprocess.Popen("pip install --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = updatePip.communicate()
        if not stderr:
            print("pip tool updated!")
    except:
        pass
    try:
        updatePip = subprocess.Popen("pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = updatePip.communicate()
        if not stderr:
            print("Python modules on Google Drive are installed!")
    except:
        pass

def downloadNotes():
    try:
        upload = subprocess.Popen("{0} {1} download".format(sys.executable, os.path.join("plugins", "NotesUtility", "access_google_drive.py")), shell=True)
        *_, stderr = upload.communicate()
        if not stderr:
            config.mainWindow.displayMessage("Restored!")
        else:
            config.mainWindow.displayMessage("Failed to download bible notes!")
    except:
        config.mainWindow.displayMessage("Failed to download bible notes!")

credentials = os.path.join("plugins", "NotesUtility", "credentials.json")
if not os.path.isfile(credentials):
    print("Turn ON Goolge Drive API first!  You need to download 'credentials.json' from https://developers.google.com/drive/api/v3/quickstart/python and place it in UniqueBible root directory.")
else:
    if not modulesInstalled:
        print("Installing missing modules ...")
        installGoogleDriveModules()
        downloadNotes()
    else:
        downloadNotes()
