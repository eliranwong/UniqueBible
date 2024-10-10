import os

thisFolder = os.getcwd()

zipFolder = os.path.join(thisFolder, "zips")

for item in os.listdir(zipFolder):
    zipFile = os.path.join(zipFolder, item)
    if os.path.isfile(zipFile) and item.endswith(".zip"):
        newZipFile = os.path.join(thisFolder, item)
        os.system(f"mv {zipFile} {newZipFile}")
        os.system(f"git add {item}")
        os.system(f"git commit -m 'upload {item}'")
        os.system("git push -u origin main")
