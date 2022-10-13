# Command Customisation

From version 32.59, two types of command entries can be customised:

* action cancellation entry
* command shortcuts

# Action Cancellation Entry

    Use config.terminal_cancel_action to customise the entry to cancel action in prompts.

# Command Shortcuts

Users can customise command shortcuts, by editing the following values:

    config.terminal_dot_a
    config.terminal_dot_b
    config.terminal_dot_c
    ...
    config.terminal_dot_x
    config.terminal_dot_y
    config.terminal_dot_z

for examples, 

* in order to set up an alias '.l' to run command '.latestbible', set config.terminal_dot_l = '.latestbible')

* in order to set up an alias '.m' to run command '.menu', set config.terminal_dot_m = '.menu')