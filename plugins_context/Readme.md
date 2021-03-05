UBA plugins for use with right-click context menu are placed in this directory.

A valid plugin file should be a python script with file extension ".py".

# config.pluginContext

The text selected by user before a right-click is assigned to config.pluginContext, with which plugin could process selected text.

# An example

A context plugin could be as simple as below, to display selected text in a dialog window.

> import config

> config.mainWindow.displayMessage(config.pluginContext)
