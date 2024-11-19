import subprocess, platform

def installmodule(module, update=True):
    #executablePath = os.path.dirname(sys.executable)
    #pippath = os.path.join(executablePath, "pip")
    #pip = pippath if os.path.isfile(pippath) else "pip"
    #pip3path = os.path.join(executablePath, "pip3")
    #pip3 = pip3path if os.path.isfile(pip3path) else "pip3"

    isInstalled, _ = subprocess.Popen("pip3 -V", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if isInstalled:

        if update:
            from uniquebible import config
            if not config.pipIsUpdated:
                pipFailedUpdated = "pip tool failed to be updated!"
                try:
                    # Update pip tool in case it is too old
                    updatePip = subprocess.Popen("python -m pip install --upgrade pip" if platform.system() == "Windows" else "pip3 install --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    *_, stderr = updatePip.communicate()
                    if not stderr:
                        print("pip tool updated!")
                    else:
                        print(pipFailedUpdated)
                except:
                    print(pipFailedUpdated)
                config.pipIsUpdated = True
        try:
            print("Installing '{0}' ...".format(module))
            installNewModule = subprocess.Popen(f"pip3 install --no-cache-dir {module}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = installNewModule.communicate()
            if not stderr:
                print("Module '{0}' is installed!".format(module))
            else:
                print(stderr)
            return True
        except:
            return False

    else:

        print("pip3 command is not found!")
        return False

