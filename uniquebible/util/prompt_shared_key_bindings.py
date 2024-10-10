from uniquebible import config
from prompt_toolkit.key_binding import KeyBindings
from uniquebible.util.ConfigUtil import ConfigUtil


prompt_shared_key_bindings = KeyBindings()

# selection

# select all
@prompt_shared_key_bindings.add("c-a")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = 0
    buffer.start_selection()
    buffer.cursor_position = len(buffer.text)

# navigation

# go to current line starting position
@prompt_shared_key_bindings.add("c-j")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position - buffer.document.cursor_position_col
# go to current line ending position
@prompt_shared_key_bindings.add("c-e")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
# go to current line starting position
@prompt_shared_key_bindings.add("home")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position - buffer.document.cursor_position_col
# go to current line ending position
@prompt_shared_key_bindings.add("end")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
# go to the end of the text
@prompt_shared_key_bindings.add("escape", "e")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = len(buffer.text)
# go to the beginning of the text
@prompt_shared_key_bindings.add("escape", "j")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = 0

# delete after cusor
@prompt_shared_key_bindings.add("c-d")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.delete(1)

# swap color theme
@prompt_shared_key_bindings.add("escape", "s")
def _(_):
    ConfigUtil.swapTerminalColors()


# clipboard

# copy text to clipboard
@prompt_shared_key_bindings.add("c-c")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.copy_selection()
    #get_app().clipboard.set_data(data)
    config.mainWindow.copy(data.text, False)
# paste clipboard text
@prompt_shared_key_bindings.add("c-v")
def _(event):
    buffer = event.app.current_buffer
    buffer.cut_selection()
    buffer.insert_text(config.mainWindow.getclipboardtext(False))
# cut text to clipboard
@prompt_shared_key_bindings.add("c-x")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.cut_selection()
    #get_app().clipboard.set_data(data)
    config.mainWindow.copy(data.text, False)

# change text

# delete text, Ctrl+H or Backspace
@prompt_shared_key_bindings.add("c-h")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.cut_selection()
    # delete one char before cursor as Backspace usually does when there is no text selection.
    if not data.text and buffer.cursor_position >= 1:
        buffer.start_selection()
        buffer.cursor_position = buffer.cursor_position - 1
        buffer.cut_selection()

# binded in this set
#a, j, e, c, v, x, h, i