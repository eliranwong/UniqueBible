from __future__ import print_function
import pickle, io, sys
import os.path
from shutil import copyfile
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


# API: https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html

# If modifying these scopes, delete the file token.pickle.
# Read options of scopes at https://developers.google.com/drive/api/v3/about-auth
#SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ["https://www.googleapis.com/auth/drive"]

noteFile = os.path.join(os.getcwd(), "marvelData", "note.sqlite")
noteFileCloudId = os.path.join("plugins", "NotesUtility", "noteFileGoogleCloudId.txt")

def getService():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
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
    # query: https://developers.google.com/drive/api/v3/search-files
    results = service.files().list(q="name='note.sqlite'", fields="files(id, name)").execute()
    items = results.get('files', [])
    return [item["id"] for item in items]

def uploadNotes(service):
    # Check cloud id of old notes
    oldFile_id = ""
    if os.path.isfile(noteFileCloudId):
        with open(noteFileCloudId, "r", encoding="utf-8") as fileObject:
            oldFile_id = fileObject.readline().rstrip()
    
    # Check if an older version exists
    currentFiles = listFiles(service)
    fileExists = oldFile_id in currentFiles

    file_metadata = {
        "name": "note.sqlite",
    }
    # sqlite3 mimetype: http://fileformats.archiveteam.org/wiki/DB_(SQLite)
    # others: https://www3.sqlite.org/src/mimetype_list
    media = MediaFileUpload(noteFile,
                            mimetype="application/x-sqlite3",
                            resumable=True)
    # update an existing file / create a new file
    if fileExists:
        file = service.files().update(fileId=oldFile_id, body=file_metadata, media_body=media, fields='id').execute()
    else:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    # Return new file id
    print(file.get('id'))

def downloadNotes(service):
    with open(noteFileCloudId, "r", encoding="utf-8") as fileObject:
        file_id = fileObject.readline().rstrip()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        downloadPercentage = int(status.progress() * 100)
        print("Downloaded {0}%".format(downloadPercentage))
    if downloadPercentage == 100:
        # Backup an earlier version
        copyfile(noteFile, "{0}_backup".format(noteFile))
        # Write a new file
        with open(noteFile, "wb") as f:
            f.write(fh.getbuffer())


if __name__ == '__main__':
    argument = " ".join(sys.argv[1:])
    service = getService()
    options = {
        "upload": uploadNotes,
        "download": downloadNotes,
    }
    if argument in options:
        options[argument](service)
