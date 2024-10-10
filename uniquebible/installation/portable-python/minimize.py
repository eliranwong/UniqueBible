import glob
import os
import re

deleteImages = True
deleteEmptyDirs = True

if os.path.exists('./htmlResources'):
    pass
elif os.path.exists('../../htmlResources'):
    os.chdir('../../')
else:
    print('Cannot find base dir')
    exit(1)

print('Minimizing ' + os.getcwd())

if deleteImages:
    imagesUsed = []
    with open('patches.txt') as f:
        lines = f.readlines()
    for line in lines:
        if "htmlResources/material/" in line and ".png" in line:
            match = re.search(r'"file", "(.*)"', line).groups()
            if match:
                image = match[0]
                imagesUsed.append(image)

    count = 0
    for filename in glob.iglob('htmlResources/material/**/**', recursive=True):
        if 'png' in filename and not os.path.isdir(filename):
            if filename not in imagesUsed:
                os.remove(filename)
                print('removing ' + filename)
                count = count + 1
                # if count > 50000:
                #     exit();
            else:
                pass
                # print('keeping ' + filename)

if deleteEmptyDirs:
    for dirpath, _, _ in os.walk("htmlResources/material/", topdown=False):
        if dirpath == "htmlResources/material/":
            break
        try:
            os.rmdir(dirpath)
            print("Deleted " + dirpath)
        except OSError:
            pass

print('Done')
