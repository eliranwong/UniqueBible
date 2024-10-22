#!/usr/bin/env python3

import os, sys, subprocess, platform, ctypes
from shutil import copyfile
from uniquebible.install.module import *

# requires python 3.7+
if sys.version_info < (3, 7):
    print("Required python version [3.7 or above] is not found!")
    print("Closing ...")
    exit(1)

def main():
    # set enviornment variables
    os.environ["PYTHONUNBUFFERED"] = "1"

    # check running mode and initial command
    runMode = sys.argv[1] if len(sys.argv) > 1 else ""
    enableCli = True if runMode.lower() in ("stream", "cli", "cli.py", "gui", "terminal", "docker", "telnet-server", "http-server", "execute-macro", "api-server") else False
    initialCommand = input("Enter command: ").strip() if runMode == "-i" else " ".join(sys.argv[1:]).strip()
    initialCommand = initialCommand.strip()

    # define directories
    # set working directory
    thisFile = os.path.realpath(__file__)
    wd = os.path.dirname(thisFile)
    if os.getcwd() != wd:
        os.chdir(wd)

    thisOS = platform.system()
    if thisOS == "Windows":
        myappid = "uniquebible.app"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        icon_path = os.path.abspath(os.path.join(sys.path[0], "htmlResources", "UniqueBibleApp.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(icon_path)

    # Do NOT use sys.executable directly
    python = os.path.basename(sys.executable)
    mainFile = os.path.join(wd, "main.py")
    major, minor, micro, *_ = sys.version_info
    cpu = ""
    if thisOS == "Darwin":
        thisOS = "macOS"
        *_, cpu = platform.mac_ver()
        cpu = f"_{cpu}"
    venvDir = "venv_{0}{4}_{1}.{2}.{3}".format(thisOS, major, minor, micro, cpu)
    binDir = "Scripts" if thisOS == "Windows" else "bin"

    # Check if virtual environment is being used
    """if sys.prefix == sys.base_prefix:
        # Check if virtual environment is available
        venvPython = os.path.join(wd, venvDir, binDir, python)
        if not os.path.exists(venvPython):
            # Installing virtual environment
            # https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
            try:
                import venv
            except:
                installmodule("virtualenv", False)
            #subprocess.Popen([python, "-m", "venv", venvDir])
            print("Setting up environment ...")
            # optional: add file "use_system_site_packages" in UBA direcyory to use packages installed on system
            try:
                if not "venv" in sys.modules:
                    import venv
                venv.create(env_dir=venvDir, with_pip=True, system_site_packages=True) if runMode == "docker" or os.path.isfile("use_system_site_packages") else venv.create(env_dir=venvDir, with_pip=True)
            except:
                pass"""

    # create shortcut files
    # On Windows
    if thisOS == "Windows":
        desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcutDir = desktopPath if os.path.isdir(desktopPath) else wd
        # gui mode shortcut
        shortcutBat1 = os.path.join(shortcutDir, "UniqueBibleApp.bat")
        shortcutCommand1 = f'''powershell.exe -NoExit -Command "python '{thisFile}'"'''
        # terminal mode shortcut
        shortcutBat2 = os.path.join(shortcutDir, "UniqueBibleAppTerminal.bat")
        shortcutCommand2 = f'''powershell.exe -NoExit -Command "python '{thisFile}' terminal"'''
        windowsShortcuts = {
            shortcutBat1: shortcutCommand1,
            shortcutBat2: shortcutCommand2,
        }
        # Create .bat for application shortcuts
        for shortcutBat, shortcutCommand in windowsShortcuts.items():
            if not os.path.isfile(shortcutBat):
                try:
                    with open(shortcutBat, "w") as fileObj:
                        fileObj.write(shortcutCommand)
                except:
                    pass
    # On non-Windows platforms
    else:
        # Create application shortcuts and set file permission
        shortcutSh = os.path.join(wd, "uba.sh")
        if not os.path.exists(shortcutSh):
            # Create .sh shortcut
            with open(shortcutSh, "w") as fileObj:
                fileObj.write("#!{0}\n{1} {2} gui".format(os.environ["SHELL"], sys.executable, thisFile))
            # Set permission
            for file in (thisFile, "main.py", "util/BibleVerseParser.py", "util/RegexSearch.py", shortcutSh):
                try:
                    os.chmod(file, 0o755)
                except:
                    pass
    # desktop shortcut on macOS
    # on iOS a-Shell app, ~/Desktop/ is invalid
    if thisOS == "macOS" and os.path.isdir("~/Desktop/"):
        app = "UniqueBibleApp"
        shortcut_file = os.path.expanduser(f"~/Desktop/{app}.command")
        if not os.path.isfile(shortcut_file):
            thisFile = os.path.realpath(__file__)
            wd = os.path.dirname(thisFile)
            appFile = "uba.py"
            icon_path = os.path.abspath(os.path.join("htmlResources", f"{app}.icns"))
            with open(shortcut_file, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"cd {wd}\n")
                f.write(f"{python} {appFile} gui\n")
            """ # This method does not work with *.command file
            # icon needs to be manually added by dragging an icon to file info
            icon_path = os.path.abspath(os.path.join("icons", f"{appName}.icns"))
            def set_icon(file_path, icon_path):
                import subprocess
                subprocess.call(['sips', '-i', icon_path, '--out', f'{file_path}/Icon\r'])
                subprocess.call(['/usr/bin/SetFile', '-a', 'C', file_path])
            set_icon(shortcut_file, icon_path)"""
            os.chmod(shortcut_file, 0o755)
    # desktop shortcuts on Linux
    elif thisOS == "Linux":
        def desktopFileContent():
            iconPath = os.path.join(wd, "htmlResources", "UniqueBibleApp.png")
            return """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Path={0}
Exec={1} {2}
Icon={3}
Name=Unique Bible App
""".format(wd, sys.executable, thisFile, iconPath)

        ubaLinuxDesktopFile = os.path.join(wd, "UniqueBibleApp.desktop")
        if not os.path.exists(ubaLinuxDesktopFile):
            # Create .desktop shortcut
            with open(ubaLinuxDesktopFile, "w") as fileObj:
                fileObj.write(desktopFileContent())
            try:
                # Try to copy the newly created .desktop file to:
                from pathlib import Path
                # ~/.local/share/applications
                userAppDir = os.path.join(str(Path.home()), ".local", "share", "applications")
                userAppDirShortcut = os.path.join(userAppDir, "UniqueBibleApp.desktop")
                if not os.path.exists(userAppDirShortcut):
                    Path(userAppDir).mkdir(parents=True, exist_ok=True)
                    copyfile(ubaLinuxDesktopFile, userAppDirShortcut)
                # ~/Desktop
                homeDir = os.environ["HOME"]
                desktopPath = f"{homeDir}/Desktop"
                desktopPathShortcut = os.path.join(desktopPath, "UniqueBibleApp.desktop")
                if os.path.exists(desktopPath) and not os.path.exists(desktopPathShortcut):
                    copyfile(ubaLinuxDesktopFile, desktopPathShortcut)
            except:
                pass

    # Run main.py
    if thisOS == "Windows":
        if python.endswith(".exe"):
            python = python[:-4]
        # Activate virtual environment
        activator = os.path.join(wd, venvDir, binDir, "activate")
        # Run main.py
        mainPy = "main.py {0}".format(initialCommand) if initialCommand else "main.py"
        if enableCli:
            if os.path.exists(activator):
                os.system("{0} & {1} {2}".format(activator, python, mainPy))
            else:
                os.system("{0} {1}".format(python, mainPy))
        else:
            if os.path.exists(activator):
                subprocess.Popen("{0} & {1} {2}".format(activator, python, mainPy), shell=True)
            else:
                subprocess.Popen("{0} {1}".format(python, mainPy), shell=True)
    else:
        """# Activate virtual environment
        activator = os.path.join(wd, venvDir, binDir, "activate_this.py")
        if not os.path.exists(activator):
            copyfile("activate_this.py", activator)
        with open(activator) as f:
            code = compile(f.read(), activator, 'exec')
            exec(code, dict(__file__=activator))"""
        # Run main.py
        if enableCli:
            os.system("{0} {1}{2}".format(python, mainFile, f" {initialCommand}" if initialCommand else ""))
        else:
            subprocess.Popen([python, mainFile, initialCommand] if initialCommand else [python, mainFile])

if __name__ == '__main__':
    main()