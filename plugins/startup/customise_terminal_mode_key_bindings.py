import config

if config.runMode == "terminal":

    from prompt_toolkit.application import run_in_terminal

    # read more about key bindings at https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html

    # press b followed by 1
    @config.key_bindings.add('escape', '1')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(f"TEXT:::{config.favouriteBible}"))

    # press b followed by 2
    @config.key_bindings.add('escape', '2')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(f"TEXT:::{config.favouriteBible2}"))

    # press b followed by 3
    @config.key_bindings.add('escape', '3')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(f"TEXT:::{config.favouriteBible3}"))