import os
import re
import sys
import requests

from uniquebible.util.UpdateUtil import UpdateUtil


def download(missingFile):
    try:
        if not re.search(r"\.(bible)|(py)|(sh)|(sqlite)|(txt)$", missingFile):
            missingFile = missingFile.replace(".", "/")
            missingFile += ".py"
        localPath = os.path.join(*missingFile.split("/"))
        requestObject2 = requests.get("{0}{1}".format(UpdateUtil.repository, missingFile))
        with open(localPath, "wb") as fileObject:
            fileObject.write(requestObject2.content)
    except Exception as e:
        print(str(e))

def printInstructions():
    print("To download a file, run:")
    print("python3 download.py <missing file module>")
    print("Examples:")
    print("python3 download.py gui.InfoDialog")
    print("python3 download.py gui/InfoDialog.py")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        download(sys.argv[1])
        print("Done")
    else:
        printInstructions()
