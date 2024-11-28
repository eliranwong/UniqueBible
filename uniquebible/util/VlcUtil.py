from uniquebible import config
import os, sys, re, platform, subprocess


class VlcUtil:

    @staticmethod
    def isPackageInstalled(package):
        whichCommand = "where.exe" if platform.system() == "Windows" else "which"
        try:
            isInstalled, *_ = subprocess.Popen("{0} {1}".format(whichCommand, package), shell=True, stdout=subprocess.PIPE).communicate()
            return True if isInstalled else False
        except:
            return False

    @staticmethod
    def openVlcPlayer():
        def run(command):
            os.system("{0}{1} > /dev/null 2>&1 &".format("nohup " if VlcUtil.isPackageInstalled("nohup") else "", command))
        VlcUtil.closeVlcPlayer()
        try:
            if config.windowsVlc:
                os.system(config.windowsVlc)
            elif config.macVlc:
                run(config.macVlc)
            elif VlcUtil.isPackageInstalled("vlc"):
                run("vlc")
        except:
            if hasattr(config, "mainWindow"):
                config.mainWindow.displayMessage(config.thisTranslation["noMediaPlayer"])

    @staticmethod
    def closeVlcPlayer():
        try:
            if platform.system() == "Windows":
                os.system("taskkill /IM vlc.exe /F")
            else:
                os.system("pkill VLC")
                os.system("pkill vlc")
        except:
            pass

    @staticmethod
    def playMediaFile(filePath, vlcSpeed, audioGui=False):
        # on macOS
        if not hasattr(config, "macVlc"):
            macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
            config.macVlc = macVlc if platform.system() == "Darwin" and os.path.isfile(macVlc) else ""
        # on Windows
        if not hasattr(config, "windowsVlc"):
            windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'

            if platform.system() == "Windows":
                if os.path.isfile(windowsVlc):
                    config.windowsVlc = windowsVlc
                elif VlcUtil.isPackageInstalled("vlc"):
                    # Windows users can install vlc command with scoop
                    # read: https://github.com/ScoopInstaller/Scoop
                    # instll scoop
                    # > iwr -useb get.scoop.sh | iex
                    # > scoop install aria2
                    # install vlc
                    # > scoop bucket add extras
                    # > scoop install vlc
                    config.windowsVlc = "vlc"
                else:
                    config.windowsVlc = ""
        # get full path and escape double quote
        if isinstance(filePath, str):
            filePath = os.path.abspath(filePath).replace('"', '\\"')
        else:
            # when filePath is a list
            filePath = [os.path.abspath(i).replace('"', '\\"') for i in filePath]
            filePath = '" "'.join(filePath)
        VlcUtil.playMediaFileVlcGui(filePath, vlcSpeed) if re.search("(.mp4|.avi)$", filePath.lower()[-4:]) or audioGui else VlcUtil.playMediaFileVlcNoGui(filePath, vlcSpeed)

    # play audio file with vlc without gui
    @staticmethod
    def playMediaFileVlcNoGui(filePath, vlcSpeed):
        try:
            # vlc on macOS
            if config.macVlc:
                command = f'''{config.macVlc} --intf rc --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
            # vlc on windows
            elif config.windowsVlc:
                command = f'''"{config.windowsVlc}" --intf dummy --play-and-exit --rate {vlcSpeed} "{filePath}"'''
            # vlc on other platforms
            elif VlcUtil.isPackageInstalled("cvlc"):
                command = f'''cvlc --no-loop --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
            # use .communicate() to wait for the playback to be completed as .wait() or checking pid existence does not work
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except:
            pass

    # play video file with vlc with gui
    @staticmethod
    def playMediaFileVlcGui(filePath, vlcSpeed):
        try:
            # vlc on macOS
            if config.macVlc:
                command = f'''{config.macVlc} --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
            # vlc on windows
            elif config.windowsVlc:
                command = f'''"{config.windowsVlc}" --play-and-exit --rate {vlcSpeed} "{filePath}"'''
            # vlc on other platforms
            elif VlcUtil.isPackageInstalled("vlc"):
                command = f'''vlc --no-loop --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
            # use .communicate() to wait for the playback to be completed as .wait() or checking pid existence does not work
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except:
            pass

if __name__ == '__main__':
    speed = float(sys.argv[1])
    audioFile = " ".join(sys.argv[2:])
    VlcUtil.playMediaFile(audioFile, speed)
    isVlcPlaying = os.path.join("temp", "isVlcPlaying")
    if os.path.isfile(isVlcPlaying):
        os.remove(isVlcPlaying)

