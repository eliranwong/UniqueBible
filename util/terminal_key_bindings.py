import config
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal

key_bindings = KeyBindings()

# add key bindings from Ctrl+A to Ctrl+Y, skipping Ctrl+D, E, H, J, M, N, O, P, T, V
if config.terminal_ctrl_a.strip():
    @key_bindings.add("c-a")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_a
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_b.strip():
    @key_bindings.add("c-b")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_b
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_c.strip():
    @key_bindings.add("c-c")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_c
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_f.strip():
    @key_bindings.add("c-f")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_f
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_g.strip():
    @key_bindings.add("c-g")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_g
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_i.strip():
    @key_bindings.add("c-i")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_i
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_k.strip():
    @key_bindings.add("c-k")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_k
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_l.strip():
    @key_bindings.add("c-l")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_l
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_r.strip():
    @key_bindings.add("c-r")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_r
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_s.strip():
    @key_bindings.add("c-s")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_s
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_u.strip():
    @key_bindings.add("c-u")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_u
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_w.strip():
    @key_bindings.add("c-w")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_w
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_x.strip():
    @key_bindings.add("c-x")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_x
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_y.strip():
    @key_bindings.add("c-y")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_y
        event.app.current_buffer.validate_and_handle()

# Ctrl+Q reserves for quiting UBA
@key_bindings.add("c-q")
def _(event):
    event.app.current_buffer.text = ".quit"
    event.app.current_buffer.validate_and_handle()

# Ctrl+Q reserves for restarting UBA
@key_bindings.add("c-z")
def _(event):
    event.app.current_buffer.text = ".restart"
    event.app.current_buffer.validate_and_handle()

