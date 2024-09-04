import hashlib
from datetime import timezone, datetime

import config

if __name__ == "__main__":
    print(f"Username: {config.apiServerClientId}")

    dt = datetime.now(timezone.utc)
    secret = config.apiServerClientSecret + str(dt.month)
    password = hashlib.md5(secret.encode("utf-8")).hexdigest()
    print(f"Password: {password}")
