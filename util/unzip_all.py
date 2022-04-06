import os

thisFolder = os.getcwd()

for item in os.listdir(thisFolder):
    zipFile = os.path.join(thisFolder, item)
    if os.path.isfile(zipFile) and item.endswith(".zip"):
        os.system(f"unzip {zipFile}")
