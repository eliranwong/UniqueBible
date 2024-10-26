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

def uploadFiles():
    from plugins.menu.GoogleDriveUtility.access_google_drive import convertFilePath
    message = ""
    try:
        filesToBackupFile = os.path.join(config.packageDir, "plugins", "menu", "GoogleDriveUtility", "my_files_to_backup.txt")
        if not os.path.exists(filesToBackupFile):
            filesToBackupFile = os.path.join(config.packageDir, "plugins", "menu", "GoogleDriveUtility", "files_to_backup.txt")
        filesToBackupList = []
        if os.path.exists(filesToBackupFile):
            with open(filesToBackupFile) as input:
                filesToBackupList = [line.strip() for line in input.readlines()]
        else:
            message = f"Please configure {filesToBackupFile}"
        for file in filesToBackupList:
            if not os.path.exists(file):
                message += f"{file} does not exist\n"
            else:
                print(f"Backing up {file}")
                fileCloudId = os.path.join(config.packageDir, "plugins", "menu", "GoogleDriveUtility", convertFilePath(file))
                upload = subprocess.Popen("{0} {1} upload {2}".format(sys.executable, os.path.join(config.packageDir, "plugins", "menu", "GoogleDriveUtility", "access_google_drive.py"), file), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = upload.communicate()
                if not stderr:
                    text = stdout.decode("utf-8")
                    if text.startswith("Please visit this URL"):
                        text = "{0}\n".format(text.split("\n")[1])
                    with open(fileCloudId, "w") as f:
                        f.write(text)
                    message += f"Uploaded {file}\n"
                else:
                    print("Error: {0} {1} upload {2}".format(sys.executable,
                      os.path.join(config.packageDir, "plugins", "menu",
                       "GoogleDriveUtility",
                       "access_google_drive.py"), file))
                    print(stderr)
                    message += f"Could not upload {file}\n"
    except Exception as ex:
        print(ex)
        message = "Failed to upload: " + ex
    config.mainWindow.displayMessage(message)


credentials = os.path.join("credentials.json")
if not os.path.isfile(credentials):
    config.mainWindow.displayMessage("You have not yet enabled Google Drive API! \nRead for more information at: https://github.com/eliranwong/UniqueBible/wiki/Backup-with-Google-Drive")
    config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/Backup-with-Google-Drive")
else:
    if not modulesInstalled:
        print("Installing missing modules ...")
        installGoogleDriveModules()
        uploadFiles()
    else:
        uploadFiles()
