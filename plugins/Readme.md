UBA plugins are placed in this directory.

A valid plugin file should be a python script with file extension ".py".

# An example

A context plugin could be as simple as below, to display a message in a dialog window.

> import config

> config.mainWindow.displayMessage("Testing a plugin!")
