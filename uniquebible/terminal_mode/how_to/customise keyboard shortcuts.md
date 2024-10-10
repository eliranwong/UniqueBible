# Customise Keyboard Shortcuts

You can cutsomise keyboard shortcuts (i.e. key bindings) for main command prompt entry via:

1. Configuration settings
2. Startup plugins

# Configuration Settings

The following key combinations:

ctrl+a, ctrl+b, ctrl+c, ctrl+f, ctrl+g, ctrl+i, ctrl+k, ctrl+l, ctrl+r, ctrl+s, ctrl+u, ctrl+w, ctrl+x, ctrl+y

can excecute commands specified in the following configuration settings:

terminal_ctrl_a, terminal_ctrl_b, terminal_ctrl_c, terminal_ctrl_f, terminal_ctrl_g, terminal_ctrl_i, terminal_ctrl_k, terminal_ctrl_l, terminal_ctrl_r, terminal_ctrl_s, terminal_ctrl_u, terminal_ctrl_w, terminal_ctrl_x, terminal_ctrl_y

To make changes, run:

> .change terminal mode config

To display current customised keyboard shortcuts, run:

> .keys

# Startup Plugins

You may customise more key bindings via startup plugins.

For an example, read the file 'plugins/startup/customise_terminal_mode_key_bindings.py'

In this plugin example, we add three keyboard shortcuts "F1", "F2" and "F3", to open users favourite bibles, defined in config.favouriteBible, config.favouriteBible2, config.favouriteBible3.

Read more at: https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html
