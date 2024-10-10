import os
from uniquebible import config
from uniquebible.util.NetworkUtil import NetworkUtil

def qrCodeCmd(command, source):
    if config.enableHttpServer:
        command = "{0}/{1}?cmd={2}".format(config.webUBAServer, config.webHomePage, command)
        return qrCode(command, source)
    else:
        return ("", "", {})

def qrCode(command, source):
    if not ("Qrcode" in config.enabled) or not ("Pillow" in config.enabled):
        return ("", "", {})

    import qrcode

    aliases = {
        "uba": "https://github.com/eliranwong/UniqueBible",
        "wiki": "https://github.com/eliranwong/UniqueBible/wiki"
    }

    cmd = command.lower().strip()
    if cmd in ["", "http-server", "http", "server"]:
        #data = "http://{0}:{1}".format(NetworkUtil.get_ip(), config.thisHttpServerPort if hasattr(config, "thisHttpServerPort") else config.httpServerPort)
        data = config.webUBAServer
    elif cmd in aliases.keys():
        data = aliases[cmd]
    else:
        data = command
    searchReplace = {
        (" ", "%20"),
        ("'", "%27"),
        ('"', "%22"),
    }
    for search, replace in searchReplace:
        data = data.replace(search, replace)
    #img = qrcode.make(data, image_factory=qrcode.image.pure.PymagingImage)
    img = qrcode.make(data)
    qrCodeFile = os.path.join(".", "htmlResources", "images", "qrcode.png")
    #qrCodeStream = open(qrCodeFile, "wb")
    #img.save(qrCodeStream)
    #qrCodeStream.close()
    img.save(qrCodeFile)
    if config.enableHttpServer:
        link = "<a href='{0}' target='_blank'>{0}</a>".format(data)
        copyAction = 'copyTextToClipboard("{0}")'.format(data)
    else:
        link = """<ref onclick="document.title='_website:::{0}'">{0}</ref>""".format(data)
        copyAction = 'document.title="_copy:::{0}"'.format(data)
    #content = "<p><img style='position:absolute;margin:auto;top:0;left:0;right:0;bottom:0;max-width:100%;height:auto;' src='./images/qrcode.png'></p>"
    content = """<p style='text-align: center;'>{0} <button type='button' title='{2}' class='ubaButton' onclick='{1}'><span class="material-icons-outlined">content_copy</span></button></p><p style='text-align: center;'><img style='margin:auto;top:0;left:0;right:0;bottom:0;max-width:100%;height:auto;' src='./images/qrcode.png'></p>""".format(link, copyAction, config.thisTranslation["context1_copy"])
    target = "main" if source == "http" else "popover.{0}".format(source)
    return (target, content, {})

config.mainWindow.textCommandParser.interpreters["qrcode"] = (qrCode, """
# [KEYWORD] QRCODE
# Display QR CODE of http-server address or text
# Usage - QRCODE:::server
# Usage - QRCODE:::[Text to convert to QR Code]
""")
config.mainWindow.textCommandParser.interpreters["_qr"] = (qrCode, """
# [KEYWORD] _qr
# Shortcut version of QRCODE
""")
config.mainWindow.textCommandParser.interpreters["_qrc"] = (qrCodeCmd, """
# [KEYWORD] _qrc
# This command is created for use in http-server only.
# Shortcut version of QRCODE, for specifying a command used by uba http-server
""")
