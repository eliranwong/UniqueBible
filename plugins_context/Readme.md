# TWO Types of Plugins

There are two different plugins in UBA, UBA plugins and UBA context plugins.

Read about UBA plugins at https://github.com/eliranwong/UniqueBible/blob/master/plugins/Readme.md

Below is description on UBA context plugins.

# UBA Context Plugins

UBA context plugins are plugins used with right-click context menu.

A valid plugin file should be a python script with file extension ".py".

# File Location

All UBA context plugins are placed in folder "plugins_context" inside UniqueBible home directory.

# Enable Plugins

You need to enable this feature by checking "enablePlugins" on "Set Config Flags" window.

# config.pluginContext

The text selected by user before a right-click is assigned to config.pluginContext, with which plugin could process selected text.

# An example

A context plugin could be as simple as below, to display selected text in a dialog window.

> import config

> config.mainWindow.displayMessage(config.pluginContext)
