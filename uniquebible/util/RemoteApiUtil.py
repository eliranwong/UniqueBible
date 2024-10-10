import hashlib
import sys
from base64 import b64encode
from datetime import timezone, datetime
import requests
from uniquebible import config

# To use:
# Set config.apiServerClientId
# Set config.apiServerClientSecret
# python -m util.RemoteApiUtil password
# python -m util.RemoteApiUtil get https://bible.gospelchurch.uk/api/bible/KJV/43/3/16

def password():
    dt = datetime.now(timezone.utc)
    secret = config.apiServerClientSecret + str(dt.month)
    password = hashlib.md5(secret.encode("utf-8")).hexdigest()
    return password

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print(" password - prints api password")
        print(" get <url> - makes get call to url")
        print(" Example:")
        print("   get https://bible.gospelchurch.uk/api/bible/KJV/43/3/16")
    else:
        method = sys.argv[1].strip()
        password = password()
        if method == "password":
            print(f"Username: {config.apiServerClientId}")
            print(f"Password: {password}")
        else:
            if len(sys.argv) < 3:
                print("Missing url")
                exit(1)
            url = sys.argv[2].strip()
            if method == "get":
                print("Get: " + url)
                decoded_token = config.apiServerClientId + ":" + password
                encoded_token = b64encode(decoded_token.encode("utf-8")).decode('utf-8')
                try:
                    response = requests.get(url,
                        headers={'Authorization': 'Basic ' + encoded_token})
                    print(response.json())
                except Exception as ex:
                    print(ex)
