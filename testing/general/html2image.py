import os, sys, base64, re

arguments = sys.argv
if (len(arguments) > 1):
    inputName = " ".join(arguments[1:])
else:
    inputName = input("Enter a filename here: ")

if not os.path.isfile(inputName):
    print("ERROR! '{0}' is not a file.".format(inputName))
else:
    fileName, fileExtension = os.path.splitext(inputName)
    if fileExtension.lower() in (".htm", ".html"):
        # read a html file
        with open(inputName, "r") as fileObject:
            htmlText = fileObject.read()
            searchPattern = r'src=(["{0}])data:image/([^<>]+?);[ ]*?base64,[ ]*?([^ <>]+?)\1'.format("'")
            for counter, value in enumerate(re.findall(searchPattern, htmlText)):
                *_, ext, data = value
                binaryString = data.encode("ascii")
                binaryData = base64.b64decode(binaryString)
                with open("{0}_image{1}.{2}".format(fileName, counter + 1, ext), "wb") as fileObject2:
                    fileObject2.write(binaryData)
    else:
        print("Entered file type is not supported.")
