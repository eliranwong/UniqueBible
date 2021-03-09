import subprocess

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
