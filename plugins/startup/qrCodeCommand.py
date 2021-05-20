import os
import config
from util.NetworkUtil import NetworkUtil


def qrCode(command, source):
    if not config.isQrCodeInstalled or not config.isPillowInstalled:
        return ("", "", {})

    import qrcode

    aliases = {
        "uba": "https://github.com/eliranwong/UniqueBible",
        "wiki": "https://github.com/eliranwong/UniqueBible/wiki"
    }

    cmd = command.lower().strip()
    if cmd in ["", "http-server", "http", "server"]:
        data = "http://{0}:{1}".format(NetworkUtil.get_ip(), config.httpServerPort)
    elif cmd in aliases.keys():
        data = aliases[cmd]
    else:
        data = command
    boxSize = 12 - (10/1000) * len(data)
    if boxSize < 2:
        boxSize = 2
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=boxSize,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qrCodeFile = os.path.join(".", "htmlResources", "images", "qrcode.png")
    img.save(qrCodeFile)
    content = "<img style='position:absolute;margin:auto;top:0;left:0;right:0;bottom:0;' src='./images/qrcode.png'>"
    target = "main" if source == "http" else "popover.fullscreen"
    return (target, content, {})

config.mainWindow.textCommandParser.interpreters["qrcode"] = (qrCode, """
# [KEYWORD] QRCODE
# Display QR CODE of http-server address or text
# Usage - QRCODE:::server
# Usage - QRCODE:::[Text to convert to QR Code]
""")
config.mainWindow.textCommandParser.interpreters["_qr"] = (qrCode, """
# [KEYWORD] _QR
# Shortcut version of QRCODE
""")
