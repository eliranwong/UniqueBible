import os, requests, zipfile

file = input("Enter url here: ")
if file:
    request = requests.get(file, stream=True)
    if request.status_code == 200:
        filename = file.split("/")[-1]
        filesize = int(request.headers.get("content-length", 0))
        print("Total size: {0:6.2f} MB".format(filesize / 1024 / 1024))
        blocksize = 20480
        
        with open(filename, "wb") as content:
            i = 1
            for block in request.iter_content(blocksize):
                content.write(block)
                progress = i * blocksize / filesize * 100
                if progress <= 100:
                    print("{0:5.2f}%".format(progress))
                elif progress > 100:
                    print("100%")
                i += 1
        
        if filename.endswith(".zip"):
            zip = zipfile.ZipFile(filename, "r")
            zip.extractall()
            zip.close()
            os.remove(filename)

    else:
        print("failed to download '{0}'.".format(file))
