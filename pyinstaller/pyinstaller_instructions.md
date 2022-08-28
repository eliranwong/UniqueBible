# Using pyinstaller to create a binary executable

1. Install pyinstaller

For Windows and Mac, run:
* pip install pyinstaller

For Mac, also run:
* brew install python3-dev

2. Create binary executable

pyinstaller main.spec --noconfirm

This will create all the files in the folder dist/UBA

3. Run app

For Windows, open the dist/UBA folder in Windows explorer and double-click UBA.exe file.

For Mac, open the dist/UBA folder in Finder and double-click UBA file.
