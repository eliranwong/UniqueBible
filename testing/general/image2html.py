import os, sys, base64

arguments = sys.argv
if (len(arguments) > 1):
    inputName = " ".join(arguments[1:])
else:
    inputName = input("Enter a filename here: ")

if not os.path.isfile(inputName):
    print("ERROR! '{0}' is not a file.".format(inputName))
else:
    fileName, fileExtension = os.path.splitext(inputName)
    if fileExtension.lower() in (".png", ".jpg", ".jpeg"):
        # read a binary file
        with open(inputName, "rb") as fileObject:
            binaryData = fileObject.read()
            encodedData = base64.b64encode(binaryData)
        # write a html file
        with open("{0}.html".format(fileName), "w") as fileObj:
            fileObj.write('<img src="data:image/{2};base64,{0}" alt="{1}">'.format(encodedData.decode('ascii'), inputName, fileExtension[1:]))
    else:
        print("Entered file type is not supported.")
