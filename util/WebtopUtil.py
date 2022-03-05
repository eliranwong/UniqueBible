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
        os.system("konsole -e 'yay -Syu --noconfirm --needed {0}'".format(package))