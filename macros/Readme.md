# Macro files

Macros are files with commands in it that can be run as a single step.  This is useful for running commonly used commands.

Macros are enabled with the enableMacros flag.

Macro files are stored in the macros directory.  All macro files are text files that end in .txt.

The macro files will show up in the Macros menu item.  When you select one, it will run all the commands in the file.

## Macro file format

Lines that start with # are comments.

A line that starts with . are interpreted as a method in MainWindow.py.  Format is ". method_name param_1, param_2".

Examples:
```
. openBrowser https://marvel.bible
. bottomHalfScreenHeight
. displayMessage January verses to study
. moveWindow .2, .2
```

Everything else is interpreted as a command that can be entered in the command bar.

Examples:
```
BIBLE:::MPB:::John 1:1, Acts 1:1, Rev 1:1
Number 6:24
```
Example macro file (/macros/Example.txt):
```
# Study for January

BIBLE:::MPB:::John 1:1, Acts 1:1, Rev 1:1

. fullsizeWindow
. displayMessage January verses to study
```

## More info

https://github.com/eliranwong/UniqueBible/wiki/Macros