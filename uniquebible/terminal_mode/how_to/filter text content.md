# Filter Text Content

You can filter the latest content line by line by running:

> .filters

Enter the patterns, in regular expression, for filtering.

Each filter should be entered on a single line when filter entry is prompted.

Press Escape+Enter when finished typing in filters in multiline input.

# Examples

Example 1 - filter cross-references to read verses that contains "Jesus" in the Gospel of John:

> crossreference:::Jn 3:16

> .filters

Enter the following string as filters:
	'Jesus'
	'John '

Example 2 - filter config labels that contain "speed":

> .config

> .filters

Enter "speed" as filters

# Edit Saved Filters

Saved filters keep records of all filters previously used.

Newly used filters are saved automatically in terminal_mode/filters.txt

They are displayed each time when users run '.filters' command, for reference purpose.

Users can manually edit the saved filters by running:

> .editfilters

Save the file as terminal_mode/filters.txt and overwrite the old one when you finish editing.
