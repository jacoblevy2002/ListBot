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
    - Adds <code>arg1</code> to the list as a new line under <code>arg2</code>. By default, only works if <code>arg2</code> is present in the list once. Has additional optional arguments:
      - <code>-full</code> or <code>-f</code>: <code>arg2</code> matches will only match full lines.
      - <code>-above</code> or <code>-aa</code> : <code>arg1</code> will be added above <code>arg2</code>, rather than below.
      - <code>-all</code>: <code>arg1</code> will be added under all matches of <code>arg2</code>, no matter how many are found.
- addundernum <code>num arg1</code>
  - Adds <code>arg1</code> to the list as a new line under line number <code>num</code>.
- getnumlines
  - Returns the number of lines in this channel's list.
- remove <code>arg1</code>
  - Removes a line beginning with <code>arg1</code>. By default, only succeeds if there's only one match. Has additional optional arguments:
    - <code>-full</code> or <code>-f</code>: Only full line matches will be removed.
    - <code>-all</code> or <code>-a</code>: All matches will be removed.
- clear
  - Clears this channel's list. Has additional optional arguments:
    - <code>-status</code> or <code>-s</code>: Only remove status messages (help menu, errors, etc).
    - <code>-all</code> or <code>-a</code>: Remove lists and status messages.
- removenum <code>num</code>
  - Removes the line at the specified number.
- removewhite
  - Removes empty lines.
- replace <code>arg1</code> <code>arg2</code>
  - Replaces the line matching <code>arg1</code> with <code>arg2</code>. By default, only succeeds if there's only one matches. Has additional optional arguments:
    - <code>-full</code> or <code>-f</code>: Only full line matches will be replaced.
    - <code>-all</code> or <code>-a</code>: All matches will be replaced.
- replaceallincategory <code>arg1</code> <code>arg2</code>
  - Runs a replaceall command in every channel in the current category, and summarizes which channels had matches. Note that this can get spammy in large categories.
- replacenum <code>num</code> <code>arg1</code>
  - Replaces the line at the specified content with <code>arg1</code>.
- effect <code>arg1</code> <code>options</code>
  - Applies an effect to the given <code>arg1</code> text. The options are:
    - <code>-bold</code> or <code>-b</code>: Surrounds the text with **, making it bold.
    - <code>-italic</code> or <code>-i</code>: Surrounds the text with _, making it italic.
    - <code>-underline</code> or <code>-u</code>: Surrounds the text with __, making it underlined.
    - <code>-kill</code> or <code>-k</code>: Surrounds the text with ~~, making it struckthrough.

  - The order the options are applied is the order they're listed; e.g., using all four at once results in \~\~\_\_\_\*\*text\*\*\_\_\_\~\~.

- dm
  - DMs the user the list, leaving markdown intact.
  - Has option arguments:
    - <code>-raw</code> or <code>-r</code>: Escapes markdown characters (\\_*~:|">`)
- help
  - Sends a help menu to the current channel, listing all commands.

## Future Plans
- Transition to slash commands
	- Using <code>/</code> instead of <code>+</code> as a command prefix, per Discord's new(-ish) addition
