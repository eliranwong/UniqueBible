from uniquebible import config

if config.runMode == "terminal":

    from prompt_toolkit.application import run_in_terminal

    # read more about key bindings at https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html

    # press F1
    @config.key_bindings.add("f1")
    def _(_):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(f"TEXT:::{config.favouriteBible}"))

    # press F2
    @config.key_bindings.add("f2")
    def _(_):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(f"TEXT:::{config.favouriteBible2}"))

    # press F3
    @config.key_bindings.add("f3")
    def _(_):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(f"TEXT:::{config.favouriteBible3}"))