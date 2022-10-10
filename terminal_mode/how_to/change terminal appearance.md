# Change terminal appearance

You may change text highlights implemented in UBA terminal mode, by running:

> .changecolors

To change terminal background or text colours, you may make changes in your own terminal settings.

# Example: macOS

1) Launch "Terminal" app
2) Go to "Preferences"
3) Make changes in "Profiles" tab

# Example: Termux on Android

Install Termux:Styling, read more at:

> https://github.com/termux/termux-styling

With Termux:Styling in place, we found the following combination is nice for use:


1) Select "Google Dark" theme with Termux:Styling

2) Run .changecolors and make changes to the following settings:

    terminalPromptIndicatorColor1 = '#00AA00'
    terminalCommandEntryColor1 = '#FFD733'
    terminalPromptIndicatorColor2 = '#FFD733'
    terminalCommandEntryColor2 = '#00AA00'
    terminalHeadingTextColor = 'GREEN'
    terminalVerseNumberColor = 'YELLOW'
    terminalResourceLinkColor = 'YELLOW'
    terminalVerseSelectionBackground = 'MAGENTA'
    terminalVerseSelectionForeground = 'RESET'
    terminalSearchHighlightBackground = 'BLUE'
    terminalSearchHighlightForeground = 'RESET'
    terminalFindHighlightBackground = 'RED'
    terminalFindHighlightForeground = 'RESET'
