from uniquebible import config
from prompt_toolkit.key_binding import KeyBindings
#from prompt_toolkit.application import run_in_terminal

uba_command_prompt_key_bindings = KeyBindings()

# add key bindings from Ctrl+B to Ctrl+Y, skipping Ctrl+A, C, D, E, H, J, M, N, O, P, T, V, X

if config.terminal_ctrl_b.strip():
    @uba_command_prompt_key_bindings.add("c-b")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_b
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_f.strip():
    @uba_command_prompt_key_bindings.add("c-f")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_f
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_g.strip():
    @uba_command_prompt_key_bindings.add("c-g")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_g
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_k.strip():
    @uba_command_prompt_key_bindings.add("c-k")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_k
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_l.strip():
    @uba_command_prompt_key_bindings.add("c-l")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_l
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_r.strip():
    @uba_command_prompt_key_bindings.add("c-r")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_r
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_s.strip():
    @uba_command_prompt_key_bindings.add("c-s")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_s
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_u.strip():
    @uba_command_prompt_key_bindings.add("c-u")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_u
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_w.strip():
    @uba_command_prompt_key_bindings.add("c-w")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_w
        event.app.current_buffer.validate_and_handle()
if config.terminal_ctrl_y.strip():
    @uba_command_prompt_key_bindings.add("c-y")
    def _(event):
        event.app.current_buffer.text = config.terminal_ctrl_y
        event.app.current_buffer.validate_and_handle()

# Escape+O launch open menu
@uba_command_prompt_key_bindings.add("escape", "o")
def _(event):
    event.app.current_buffer.text = ".open"
    event.app.current_buffer.validate_and_handle()

# Escape+D run default command
@uba_command_prompt_key_bindings.add("escape", "d")
def _(event):
    event.app.current_buffer.text = ".my"
    event.app.current_buffer.validate_and_handle()

# Escape+T launch text-to-speech menu
@uba_command_prompt_key_bindings.add("escape", "t")
def _(event):
    event.app.current_buffer.text = ".speak"
    event.app.current_buffer.validate_and_handle()

# Escape+P launch plugins menu
@uba_command_prompt_key_bindings.add("escape", "p")
def _(event):
    event.app.current_buffer.text = ".plugins"
    event.app.current_buffer.validate_and_handle()

# Escape+M launch master menu
@uba_command_prompt_key_bindings.add("escape", "m")
def _(event):
    event.app.current_buffer.text = ".menu"
    event.app.current_buffer.validate_and_handle()

# Escape+H launch help menu
@uba_command_prompt_key_bindings.add("escape", "h")
def _(event):
    event.app.current_buffer.text = ".help"
    event.app.current_buffer.validate_and_handle()

# Escape+C open system command prompt
@uba_command_prompt_key_bindings.add("escape", "c")
def _(event):
    event.app.current_buffer.text = ".system"
    event.app.current_buffer.validate_and_handle()

# Ctrl+Q quit UBA
@uba_command_prompt_key_bindings.add("c-q")
def _(event):
    event.app.current_buffer.text = ".quit"
    event.app.current_buffer.validate_and_handle()

# Ctrl+Z restart UBA
@uba_command_prompt_key_bindings.add("c-z")
def _(event):
    event.app.current_buffer.text = ".restart"
    event.app.current_buffer.validate_and_handle()

# Escape+W open wordnet
@uba_command_prompt_key_bindings.add("escape", "w")
def _(event):
    event.app.current_buffer.text = ".wordnet"
    event.app.current_buffer.validate_and_handle()

# Escape+1 change bible
@uba_command_prompt_key_bindings.add("escape", "1")
def _(event):
    event.app.current_buffer.text = ".changebible"
    event.app.current_buffer.validate_and_handle()

# Escape+2 change bibles for comparison
@uba_command_prompt_key_bindings.add("escape", "2")
def _(event):
    event.app.current_buffer.text = ".changebibles"
    event.app.current_buffer.validate_and_handle()

# Escape+3 change commentary
@uba_command_prompt_key_bindings.add("escape", "3")
def _(event):
    event.app.current_buffer.text = ".changecommentary"
    event.app.current_buffer.validate_and_handle()
