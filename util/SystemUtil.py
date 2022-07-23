import os
import platform


class SystemUtil:

    @staticmethod
    def isWayland():
        if platform.system() == "Linux" and not os.getenv('QT_QPA_PLATFORM') is None and os.getenv('QT_QPA_PLATFORM') == "wayland":
            return True
        else:
            return False
