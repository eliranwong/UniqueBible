# flake8: noqa
from __future__ import print_function

import mimetypes
import pathlib
import pickle, io, sys
import os.path
import re
from shutil import copyfile
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


# API: https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html

# If modifying these scopes, delete the file token.pickle.
# Read options of scopes at https://developers.google.com/drive/api/v3/about-auth
SCOPES = ["https://www.googleapis.com/auth/drive"]

def getService():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def listFiles(service):
    folder = getBackupFolder(service)
    results = service.files().list(q=f"'{folder}' in parents", fields="files(id, name)").execute()
    items = results.get('files', [])
    return [item["id"] for item in items]

def createBackupFolder(service):
    file_metadata = {'name': 'UBA-backups', 'mimeType': 'application/vnd.google-apps.folder'}
    service.files().create(body=file_metadata, fields='id').execute()

def getBackupFolder(service):
    results = service.files().list(q="name='UBA-backups' and mimeType='application/vnd.google-apps.folder'", fields="files(id, name)").execute()
    items = results.get('files', [])
    if len(items) > 0:
        return items[0]['id']
    else:
        return 0

def uploadFiles(service):
    oldFile_id = ""
    if os.path.isfile(cloudIdFile):
        with open(cloudIdFile, "r", encoding="utf-8") as fileObject:
            oldFile_id = fileObject.readline().rstrip()

    # Check if an older version exists
    currentFiles = listFiles(service)
    fileExists = oldFile_id in currentFiles

    file_update_metadata = {
        "name": backupFile,
    }
    file_create_metadata = {
        "name": backupFile,
        "parents": [getBackupFolder(service)]
    }
    media = MediaFileUpload(backupFile,
                            mimetype=getMimeType(backupFile),
                            resumable=True)
    # update an existing file / create a new file
    if fileExists:
        file = service.files().update(fileId=oldFile_id, body=file_update_metadata, media_body=media, fields='id').execute()
    else:
        file = service.files().create(body=file_create_metadata, media_body=media, fields='id').execute()
    # Return new file id
    print(file.get('id'))

def convertFilePath(path):
    path = re.sub(r"[/\\]", "_", path)
    path += ".txt"
    return path

# mimetypes: https://www3.sqlite.org/src/mimetype_list
def getMimeType(file):
    extension = pathlib.Path(file).suffix
    if extension in [".sqlite", ".lexicon", ".data", ".commentary", ".book", ".bible"]:
        return "application/x-sqlite3"
    elif extension in [".mp3"]:
        return "audio/mpeg"
    elif extension in [".mp4"]:
        return "video/mp4"
    elif extension in [".css"]:
        return "text/css"
    elif extension in [".js"]:
        return "text/javascript"
    else:
        return mimetypes.guess_type(file)[0]

def downloadFiles(service):
    with open(cloudIdFile, "r", encoding="utf-8") as fileObject:
        file_id = fileObject.readline().rstrip()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        downloadPercentage = int(status.progress() * 100)
        # print("Downloaded {0}%".format(downloadPercentage))
    if downloadPercentage == 100:
        # Backup an earlier version
        if os.path.exists(backupFile):
            copyfile(backupFile, "{0}_backup".format(backupFile))
        # Write a new file
        with open(backupFile, "wb") as f:
            f.write(fh.getbuffer())


if __name__ == '__main__':

    service = getService()
    if getBackupFolder(service) == 0:
        createBackupFolder(service)
    argument, backupFile = " ".join(sys.argv[1:]).split(" ", 1)
    cloudIdFile = os.path.join(config.packageDir, "plugins", "menu", "GoogleDriveUtility", convertFilePath(backupFile))
    options = {
        "upload": uploadFiles,
        "download": downloadFiles,
    }
    if argument in options:
        options[argument](service)
