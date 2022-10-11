# Change terminal appearance

You may change text highlights implemented in UBA terminal mode, by running:

> .changecolors

To change terminal background or text colours, you may make changes in your own terminal settings.

# Example: macOS

1) Launch "Terminal" app
2) Go to "Preferences"
3) Make changes in "Profiles" tab

For example, choose profile "Pro", change opacity to 100% and use the following settings:

    terminalPromptIndicatorColor1 = '#FF0066'
    terminalCommandEntryColor1 = '#FFD733'
    terminalPromptIndicatorColor2 = '#33B8FF'
    terminalCommandEntryColor2 = '#00AA00'
    terminalHeadingTextColor = 'LIGHTBLUE_EX'
    terminalVerseNumberColor = 'GREEN'
    terminalResourceLinkColor = 'CYAN'
    terminalVerseSelectionBackground = 'YELLOW'
    terminalVerseSelectionForeground = 'RESET'
    terminalSearchHighlightBackground = 'GREEN'
    terminalSearchHighlightForeground = 'RESET'
    terminalFindHighlightBackground = 'MAGENTA'
    terminalFindHighlightForeground = 'RESET'

# Example: Termux on Android

Install Termux:Styling, read more at:

> https://github.com/termux/termux-styling

With Termux:Styling in place, we found the following combination is nice for use:

1) Select "Google Dark" theme with Termux:Styling

2) Run .changecolors and make changes to the following settings:

    terminalPromptIndicatorColor1 = '#FF0066'
    terminalCommandEntryColor1 = '#FFD733'
    terminalPromptIndicatorColor2 = '#33B8FF'
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
