import config
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal

key_bindings = KeyBindings()

# add key bindings from Ctrl+A to Ctrl+Y, skipping Ctrl+D, E, H, J, M, N, O, P, T, V
if config.terminal_ctrl_a.strip():
    @key_bindings.add('c-a')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_a))
if config.terminal_ctrl_b.strip():
    @key_bindings.add('c-b')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_b))
if config.terminal_ctrl_c.strip():
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
if config.terminal_ctrl_f.strip():
    @key_bindings.add('c-f')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_f))
if config.terminal_ctrl_g.strip():
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
if config.terminal_ctrl_i.strip():
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
if config.terminal_ctrl_k.strip():
    @key_bindings.add('c-k')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_k))
if config.terminal_ctrl_l.strip():
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
if config.terminal_ctrl_r.strip():
    @key_bindings.add('c-r')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_r))
if config.terminal_ctrl_s.strip():
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
if config.terminal_ctrl_u.strip():
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
if config.terminal_ctrl_w.strip():
    @key_bindings.add('c-w')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_w))
if config.terminal_ctrl_x.strip():
    @key_bindings.add('c-x')
    def _(event):
        print("")
        print(config.mainWindow.divider)
        run_in_terminal(lambda: config.runTerminalModeCommand(config.terminal_ctrl_x))
if config.terminal_ctrl_y.strip():
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

