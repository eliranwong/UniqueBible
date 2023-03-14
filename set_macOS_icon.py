import sys
import os
import base64
from xattr import xattr

def set_icon(file_path, icon_path):
    icon_data = open(icon_path, 'rb').read()
    icon_data_base64 = base64.b64encode(icon_data)
    x = xattr(file_path)
    x.set('com.apple.ResourceFork', b'data:application/octet-stream;base64,' + icon_data_base64)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_icon.py target_file icon_file")
        sys.exit(1)
    target_file = sys.argv[1]
    icon_file = sys.argv[2]

    if not os.path.exists(target_file) or not os.path.exists(icon_file):
        print("Error: One or both of the specified paths do not exist.")
        sys.exit(1)

    set_icon(target_file, icon_file)