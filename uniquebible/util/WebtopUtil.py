import os, sys, platform
import subprocess


class WebtopUtil:

    @staticmethod
    def run(command):
        if WebtopUtil.isPackageInstalled("nohup"):
            WebtopUtil.runNohup(command)
        else:
            os.system("{0} > /dev/null 2>&1 &".format(command))

    @staticmethod
    def runNohup(command):
        os.system("nohup {0} > /dev/null 2>&1 &".format(command))

    @staticmethod
    def openDir(dir):
        if os.path.isdir(dir):
            WebtopUtil.runNohup(f"thunar {dir}")
        else:
            print(f"{dir} is not a directory!")

    @staticmethod
    def openFile(filename):
        try:
            if sys.platform == "win32":
                try:
                    os.startfile(filename)
                except:
                    os.system(f"start {filename}")
            else:
                # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                if WebtopUtil.isPackageInstalled("nohup"):
                    WebtopUtil.runNohup("{0} {1}".format(opener, filename))
                else:
                    subprocess.call([opener, filename])
        except:
            print(f"Unable to open file '{filename}'!")

    @staticmethod
    def isPackageInstalled(package):
        whichCommand = "where.exe" if platform.system() == "Windows" else "which"
        try:
            isInstalled, *_ = subprocess.Popen("{0} {1}".format(whichCommand, package), shell=True, stdout=subprocess.PIPE).communicate()
            return True if isInstalled else False
        except:
            return False

    @staticmethod
    def installPackage(package):
        os.system("konsole -e 'sudo pacman -Syu --noconfirm --needed {0}'".format(package))

    @staticmethod
    def installAurPackage(package):
        if not WebtopUtil.isPackageInstalled("yay"):
            print("Installing yay ...")
            if not os.path.isdir("/opt/yay"):
                os.system("sudo git clone https://aur.archlinux.org/yay-git.git /opt/yay")
            os.system("sudo chown -R abc:users /opt/yay && cd /opt/yay && makepkg -si --noconfirm --needed && cd -")
        os.system("konsole -e 'yay -Syu --noconfirm --needed {0}'".format(package))