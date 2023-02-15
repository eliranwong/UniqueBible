import socket
import urllib.request


class NetworkUtil:

    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    @staticmethod
    def is_valid_url(url):
        try:
            import validators
            if validators.url(url):
                return True
            else:
                return False
        except:
            return True

    @staticmethod
    def check_internet_connection(url='https://www.google.com/', timeout=5):
        try:
            urllib.request.urlopen(url, timeout=timeout)
            return True
        except urllib.request.URLError:
            return False
