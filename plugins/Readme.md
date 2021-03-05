There are two different plugins in UBA, UBA plugins and UBA context plugins.

Read about UBA context plugins at https://github.com/eliranwong/UniqueBible/blob/master/plugins_context/Readme.md

Below is description on UBA plugins.

# UBA Plugins

UBA plugins are plugins accessible through menu.

A valid plugin file should be a python script with file extension ".py".

# File Location

All UBA plugins are placed in folder "plugins" inside UniqueBible home directory.

# Enable Plugins

You need to enable this feature by checking "enablePlugins" on "Set Config Flags" window.

# An example

A context plugin could be as simple as below, to display a message in a dialog window.

> import config

> config.mainWindow.displayMessage("Testing a plugin!")
