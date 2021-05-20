import os
import config
from util.NetworkUtil import NetworkUtil


def qrCode(command, source):
    if not config.isQrCodeInstalled or not config.isPillowInstalled:
        return ("", "", {})
    import qrcode
    if command.lower().strip() in ["", "http-server", "http", "server"]:
        data = "http://{0}:{1}".format(NetworkUtil.get_ip(), config.httpServerPort)
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
    return ("popover.fullscreen", content, {})

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
