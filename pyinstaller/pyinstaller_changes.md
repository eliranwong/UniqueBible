# Code changes for pyinstaller

* Add main.spec
* Add database wrapper (dbw.py) to use sqlite3 for binary run mode and apsw for Python run mode
* Add config.enableBinaryExecutionMode that is enabled when file "enable_binary_execution_mode" exists in root
* Use Starter.py for layout
* Disable code self-updating
* Disable modules 'apsw','chinese-english-lookup','word-forms','lemmagen3'
* Add config.ini support, instead of using config.py
* Fix false positive for virus

## To-do

* Add icon
* Fix loading Starter layout

## Code snippet

if config.enableBinaryExecutionMode:
