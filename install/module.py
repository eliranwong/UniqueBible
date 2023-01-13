import config, subprocess

def installmodule(module):
    #executablePath = os.path.dirname(sys.executable)
    #pippath = os.path.join(executablePath, "pip")
    #pip = pippath if os.path.isfile(pippath) else "pip"
    #pip3path = os.path.join(executablePath, "pip3")
    #pip3 = pip3path if os.path.isfile(pip3path) else "pip3"

    if not config.pipIsUpdated:
        try:
            # Update pip tool in case it is too old
            updatePip = subprocess.Popen("pip3 install --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = updatePip.communicate()
            if not stderr:
                print("pip tool updated!")
        except:
            pass
        config.pipIsUpdated = True
    try:
        print("Installing '{0}' ...".format(module))
        installNewModule = subprocess.Popen(f"pip3 install {module}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = installNewModule.communicate()
        if not stderr:
            print("Module '{0}' is installed!".format(module))
    except:
        pass
