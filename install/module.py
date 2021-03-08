import subprocess

def installmodule(module):
    try:
        # Update pip tool in case it is too old
        updatePip = subprocess.Popen("pip install --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = updatePip.communicate()
        if not stderr:
            print("pip tool updated!")
    except:
        pass
    try:
        print("Installing '{0}' ...".format(module))
        updatePip = subprocess.Popen("pip install {0}".format(module), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = updatePip.communicate()
        if not stderr:
            print("Module '{0}' is installed!".format(module))
    except:
        pass
