import os
import platform
from ast import literal_eval
import requests

import config
from util.DateUtil import DateUtil


class UpdateUtil:

    repository = "https://raw.githubusercontent.com/eliranwong/UniqueBible/master/"

    @staticmethod
    def checkIfShouldCheckForAppUpdate():
        if config.lastAppUpdateCheckDate == '':
            config.lastAppUpdateCheckDate = str(DateUtil.localDateNow())
            return False
        else:
            compareDate = DateUtil.addDays(UpdateUtil.lastAppUpdateCheckDateObject(),
                                           int(config.daysElapseForNextAppUpdateCheck))
            if compareDate <= DateUtil.localDateNow():
                return True
            else:
                return False

    @staticmethod
    def lastAppUpdateCheckDateObject():
        return DateUtil.dateStringToObject(config.lastAppUpdateCheckDate)

    @staticmethod
    def getLatestVersion():
        try:
            checkFile = "{0}UniqueBibleAppVersion.txt".format(UpdateUtil.repository)
            request = requests.get(checkFile, timeout=5)
            if request.status_code == 200:
                config.internet = True
                return request.text.strip()
            else:
                config.internet = False
        except Exception as e:
            config.internet = False
        return ""

    @staticmethod
    def getCurrentVersion():
        with open("UniqueBibleAppVersion.txt", "r", encoding="utf-8") as fileObject:
            text = fileObject.read()
            return text.strip()

    @staticmethod
    def currentIsLatest(current, latest):
        if current == '' or latest == '':
            return False
        res = float(current) >= float(latest)
        return res

    @staticmethod
    def updateUniqueBibleApp(parent=None, debug=False):
        requestObject = requests.get("{0}patches.txt".format(UpdateUtil.repository))
        for line in requestObject.text.split("\n"):
            if line:
                try:
                    version, contentType, filePath = literal_eval(line)
                    if version > config.version:
                        localPath = os.path.join(*filePath.split("/"))
                        if debug:
                            print("{0}:{1}".format(version, localPath))
                        else:
                            if contentType == "folder":
                                if not os.path.isdir(localPath):
                                    os.makedirs(localPath)
                            elif contentType == "file":
                                requestObject2 = requests.get("{0}{1}".format(UpdateUtil.repository, filePath))
                                with open(localPath, "wb") as fileObject:
                                    fileObject.write(requestObject2.content)
                except Exception as e:
                    # message on failed item
                    if parent is not None:
                        parent.displayMessage("{0}\n{1}".format(config.thisTranslation["message_fail"], line))
                    else:
                        return "Could not update"
        # set executable files on macOS or Linux
        if not platform.system() == "Windows":
            for filename in ("uba.py", "main.py", "BibleVerseParser.py", "RegexSearch.py"):
                if os.path.isfile(filename):
                    os.chmod(filename, 0o755)
                # finish message
        config.lastAppUpdateCheckDate = str(DateUtil.localDateNow())
        if parent is not None:
            parent.displayMessage(
                "{0}  {1}".format(config.thisTranslation["message_done"], config.thisTranslation["message_restart"]))
        else:
            return "Success"
