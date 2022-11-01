# Portable Python

Allows running UBA on any computer by having a complete Python interpreter and UBA code on USB stick.

Prepare USB stick:
* Verify USB has at least 16 GB free
* Rename USB stick to "UBA_USB"

Prepare UBA:
* Download [UBA.zip](https://github.com/eliranwong/UniqueBible/archive/refs/heads/main.zip)
* Unzip UBA zip onto hard disk

## Mac (M1 or x86)

Download Portable Python:
* Download [Portable Python 3.10.8](https://drive.google.com/drive/folders/12nyYAvh33ImFnU0_E1Nmv7RhQsOgMFYl)

Minimize UBA:
* In unzipped UBA folder, run `python minimize.py` to delete unused files (will delete over 84000 files)

Configure:
* Copy installation/portable-python/run*.sh to UBA root
* On hard drive, execute `run_m1.sh` (M1 Mac) or `run_x86.sh` (x86 Mac) 
* Wait while the venv directory is being created
* After UBA starts, optionally download resources

Copy to stick:
* Copy Portable Python to stick and unzip
* Rename Portable Python directory to either `3.10.8_m1` or `3.10.8_x86`
* Run `unquarantine.sh` on Portable Python files on stick
* Copy UBA zip to stick and unzip

Run UBA:
* Execute `run_m1.sh` or `run_x86.sh` on stick

Notes:
* On Mac, USB is under `/Volumes`
* On Ubuntu, USB is under `/media`

## Windows

Download Portable Python:
* Download [WinPython 3.10.8](https://github.com/winpython/winpython/releases)

Minimize UBA:
* In unzipped UBA folder, run `python minimize.py` to delete unused files (will delete over 84000 files)
* Zip the UBA folder

Copy to stick:
* Run WinPython and install the Python directory on the USB stick
* Copy UBA zip to stick and unzip

Run UBA:
* In the WinPython directory, run `WinPython Terminal.exe`
* This will open a terminal that has Python in the path
* Execute `cd D:` to go to the USB stick
* Execute `cd UniqueBible` to go into the UBA directory
* Execute `python uba.py` to start UBA
