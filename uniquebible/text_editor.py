#!/usr/bin/env python

from uniquebible import config
from uniquebible.util.text_editor_checkup import *
import argparse, sys, os
from uniquebible.util.TextEditorUtility import TextEditorUtility
from uniquebible.util.terminal_text_editor import TextEditor


class StartEditor:

    def multilineEditor(self, text="", placeholder="", filepath="", newFile=False, wd=""):
        config.textEditor = TextEditor(config.mainWindow, working_directory=wd)
        if newFile:
            return config.textEditor.newFile()
        elif filepath:
            return config.textEditor.openFile(filepath)
        return config.textEditor.multilineEditor(text, placeholder)

if __name__ == "__main__":

    config.terminalColors = {
        "ansidefault": "ansidefault",
        "ansiblack": "ansiwhite",
        "ansired": "ansibrightred",
        "ansigreen": "ansibrightgreen",
        "ansiyellow": "ansibrightyellow",
        "ansiblue": "ansibrightblue",
        "ansimagenta": "ansibrightmagenta",
        "ansicyan": "ansibrightcyan",
        "ansigray": "ansibrightblack",
        "ansiwhite": "ansiblack",
        "ansibrightred": "ansired",
        "ansibrightgreen": "ansigreen",
        "ansibrightyellow": "ansiyellow",
        "ansibrightblue": "ansiblue",
        "ansibrightmagenta": "ansimagenta",
        "ansibrightcyan": "ansicyan",
        "ansibrightblack": "ansigray",
    }

    # make sure relative path of plugins folder works
    thisFile = os.path.realpath(__file__)
    wd = os.path.dirname(thisFile)

    # make utilities available to plugins
    config.mainWindow = TextEditorUtility(working_directory=wd)

    # startup
    startup = StartEditor()

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('--filename', '-f', nargs='?')
    parser.add_argument('--text', '-t', nargs='?')
    args = parser.parse_args()
    if args.file:
        startup.multilineEditor(filepath=args.file, wd=wd)
    elif args.filename:
        startup.multilineEditor(filepath=args.filename, wd=wd)
    elif args.text:
        startup.multilineEditor(text=args.text, wd=wd)
    elif not sys.stdin.isatty():
        #text = sys.stdin.read()
        #startup.multilineEditor(text=text, wd=wd)
        parser.print_help()
    else:
        startup.multilineEditor(newFile=True, wd=wd)
