import os
import subprocess


class WebtopUtil:

    @staticmethod
    def runNohup(command):
        os.system("nohup {0} > /dev/null 2>&1 &".format(command))

    @staticmethod
    def isPackageInstalled(package):
        isInstalled, *_ = subprocess.Popen("which {0}".format(package), shell=True, stdout=subprocess.PIPE).communicate()
        return True if isInstalled else False

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