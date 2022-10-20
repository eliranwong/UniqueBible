import config
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal

key_bindings = KeyBindings()

# add key bindings from Ctrl+A to Ctrl+Y, skipping Ctrl+D, E, H, J, M, N, O, P, T, V
@key_bindings.add('c-a')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_a))
@key_bindings.add('c-b')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_b))
@key_bindings.add('c-c')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_c))
#@key_bindings.add('c-d')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_d))
#@key_bindings.add('c-e')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_e))
@key_bindings.add('c-f')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_f))
@key_bindings.add('c-g')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_g))
#@key_bindings.add('c-h')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_h))
@key_bindings.add('c-i')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_i))
#@key_bindings.add('c-j')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_j))
@key_bindings.add('c-k')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_k))
@key_bindings.add('c-l')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_l))
#@key_bindings.add('c-m')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_m))
#@key_bindings.add('c-n')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_n))
#@key_bindings.add('c-o')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_o))
#@key_bindings.add('c-p')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_p))
@key_bindings.add('c-r')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_r))
@key_bindings.add('c-s')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_s))
#@key_bindings.add('c-t')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_t))
@key_bindings.add('c-u')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_u))
#@key_bindings.add('c-v')
#def _(event):
#    print("")
#    print(config.mainWindow.divider)
#    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_v))
@key_bindings.add('c-w')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_w))
@key_bindings.add('c-x')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_x))
@key_bindings.add('c-y')
def _(event):
    print("")
    print(config.mainWindow.divider)
    run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_y))

# Ctrl+Q reserves for quiting UBA
@key_bindings.add('c-q')
def _(event):
    print("")
    config.mainWindow.quitUBA()

# Ctrl+Q reserves for restarting UBA
@key_bindings.add('c-z')
def _(event):
    print("")
    config.mainWindow.restartUBA()

