# ListBot

**ListBot** is a Discord bot designed to allow multiple users to modify the same list without needing to re-send elements or separate the list into multiple messages. ListBot only requires the user to have permission to send messages for them to modify the list.

The bot requires message reading, message content viewing, and default permissions to function.

As of now there is no way to add ListBot to your own server, but if this seems interesting please feel free to download and run the code locally. The only package required is discord.py, and the environment variable LotToken must be set to your Discord API key.

## Commands
Note that all commands are prefixed with the plus (+) symbol.<br/>
Unless otherwise specified, anything involving finding text (such as +add <code>arg1 arg2</code>) searches starting from the beginning of the line and only accepts exact matches. The search will fail if multiple matches are found.

- add <code>arg1</code>
    - Adds <code>arg1</code> to the end of the list.
- add <code>arg1 arg2</code>
    - Adds <code>arg1</code> to the list as a new line under <code>arg2</code>. Adding <code>true</code> to the command will only match full lines.
- addundernum <code>num arg1</code>
	- Adds <code>arg1</code> to the list as a new line under line number <code>num</code>.
- getnumlines
	- Returns the number of lines in this channel's list.
- remove <code>arg1</code>
	- Removes a line beginning with <code>arg1</code>. Will only succeed if there's one match. Adding <code>true</code> to the command will only match full lines.
- clear
	- Clears this channel's list. Adding <code>status</code> will instruct it to only delete status messages (help menu, errors, etc), and adding <code>all</code> will instruct it to delete both list and status messages
- removemore <code>arg1</code>
	- Removes all lines beginning with <code>arg1</code>. Adding <code>true</code> to the command will only match full lines.
- removenum <code>num</code>
	- Removes the line at the specified number.
- removewhite
	- Removes empty lines.
- replace <code>arg1</code> <code>arg2</code>
	- Replaces the line matching <code>arg1</code> with <code>arg2</code>. Fails if there are multiple matches, and accepts <code>true</code> full-line argument.
- replaceall <code>arg1</code> <code>arg2</code>
	- Replaces all instances of <code>arg1</code> with <code>arg2</code>, no matter where they occur. Think using <code>CTRL + F</code> to replace all.
- replaceallincategory <code>arg1</code> <code>arg2</code>
	- Runs a replaceall command in every channel in the current category, and summarizes which channels had matches. Note that this can get spammy in large categories.
- replacenum <code>num</code> <code>arg1</code>
	- Replaces the line at the specified content with <code>arg1</code>.
- raw
	- DMs the user the raw list, escaping markdown elements.
		- For example, **__Example__** would become \*\*\_\_Example\_\_\*\*
- dm
	- DMs the user the list, leaving markdown intact.
- help
	- Sends a help menu to the current channel, listing all commands.

## Future Plans
- Transition to slash commands
	- Using <code>/</code> instead of <code>+</code> as a command prefix, per Discord's new(-ish) addition
- Add <code>addabove</code> command
	- Two arguments; <code>LINE_TO_ADD</code> and <code>ADD_ABOVE</code>
	- Adds <code>LINE_TO_ADD</code> above the line beginning with <code>ADD_ABOVE</code>
