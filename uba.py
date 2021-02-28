import os, sys, subprocess
from shutil import copyfile

# Tested on Linux
# TODO: To be tested on macOS and Windows

# Required minimum python version: 3.7
if sys.version_info < (3, 7):
    print("UniqueBible.app runs only with Python 3.7 or later")
    exit(1)

# Set environment variable
os.environ["QT_LOGGING_RULES"] = "*=false"

#python = "py" if platform.system() == "Windows" else "python3"
# Do NOT use sys.executable directly
python = os.path.basename(sys.executable)
#print(python)
mainFile = os.path.join(os.getcwd(), "main.py")
venvDir = "venv"

def pip3IsInstalled():
    isInstalled, _ = subprocess.Popen("pip3 -V", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return isInstalled

# A method to install 
def pip3InstallModule(module):
    if not pip3IsInstalled():
        subprocess.Popen([sys.executable, "-m", "pip", "install", "--user", "--upgrade pip"])
    # run pip3IsInstalled again to check if pip3 is installed successfully for users in case they didn't have it.
    if pip3IsInstalled():
        print("Installing missing module '{0}' ...".format(module))
        # implement pip3 as a subprocess:
        install = subprocess.Popen(['pip3', 'install', module], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = install.communicate()
        return stderr
    else:
        noPip3Message = "pip3 command is not found!"
        print(noPip3Message)
        return noPip3Message

# Check if virtual environment is being used
if sys.prefix == sys.base_prefix:
    # Check if virtual environment is available
    # TODO: check if the following path works on Windows
    venvPython = os.path.join(os.getcwd(), venvDir, "bin", python)
    if not os.path.exists(venvPython):
        # Installing virtual environment
        # https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
        try:
            import venv
        except:
            pip3InstallModule("virtualenv")
        #subprocess.Popen([python, "-m", "venv", venvDir])
        print("Setting up environment ...")
        import venv
        venv.create(env_dir=venvDir, with_pip=True)
    # Check if activate script exists
    activator = os.path.join(os.getcwd(), venvDir, "bin", "activate_this.py")
    if not os.path.exists(activator):
        copyfile("activate_this.py", activator)
    with open(activator) as f:
        code = compile(f.read(), activator, 'exec')
        exec(code, dict(__file__=activator))

# Run main.py
#print(sys.prefix, sys.base_prefix)
subprocess.Popen([python, mainFile])
