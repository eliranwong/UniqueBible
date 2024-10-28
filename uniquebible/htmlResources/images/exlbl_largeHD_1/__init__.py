import os
from pathlib import Path
from shutil import copytree

thisFolder = os.path.dirname(os.path.realpath(__file__))

ubahome = os.path.expanduser(os.path.join("~", "UniqueBible"))

imageFolder = os.path.join(ubahome, "htmlResources", "images")

if not os.path.isdir(imageFolder):
    Path(imageFolder).mkdir(parents=True, exist_ok=True)

#for i in ("exlbl", "exlbl_large", "exlbl_largeHD"):
destFolder = os.path.join(imageFolder, "exlbl_largeHD")
if not os.path.isfile(os.path.join(destFolder, "BL400.png")):
    copytree(thisFolder, destFolder, dirs_exist_ok=True)
    