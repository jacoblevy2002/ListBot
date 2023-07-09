import discord
from discord.ext import commands
import os
from datetime import datetime

MESSAGE_LENGTH = 1950

_intents = discord.Intents.default()
_intents.message_content = True
_intents.messages = True
bot = commands.Bot(command_prefix="+", intents=_intents)
bot.remove_command("help")

TOKEN = os.environ["LotToken"]  # API token

LOG_FILE = "./Lot.log"


def log_message(message):
    message = message.encode('utf8')
    with open(LOG_FILE, 'a') as f:
        f.write(f"\n{datetime.now()} | {str(message)}")


def log(channel: str, category: str, command: str, author: str, arguments: list[str] = []):
    """ Log activity to the .log file """
    log_message(
        f"Command executed: {command} | Channel: {channel} (Category: {category}) | Arguments: {arguments} | Executed by: {author}")


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


async def message_over_limit(msg, channel):
    lines = msg.split("\n")

    while not lines == []:
        checked_lines = []

        while not lines == [] and len("\n".join(checked_lines) + "\n" + lines[0]) < MESSAGE_LENGTH:
            checked_lines.append(lines[0])
            lines.pop(0)

        await channel.send("\n".join(checked_lines))


def set_save_to(save_to, val):
    if isinstance(save_to, int):
        return val
    elif isinstance(save_to, list):
        save_to.append(val)
        return save_to
    else:
        return -1


async def send_list(channel, bot_messages, to_add="", to_find="", remove_or_replace: bool = False,
                    full_line_check: bool = False, add_above: bool = False, index_to_add: int = -1,
                    replace_all: bool = False, index_to_change: int = -1, allow_multiple_matches: bool = False):
    total_list = []
    for i in bot_messages:
        total_list.extend(i.content.split("\n"))

    if (to_find != "" and not replace_all) or full_line_check:  # if to_find is not empty - ie add part way through
        # default value of -1 or empty list - it can never be inserted to -1 in a msg
        save_to = [] if allow_multiple_matches else -1
        # x = -1  # starts at -1 so that first value is 0
        for i in range(len(total_list)):  # for each line in list
            # x += 1  # in Python it seems you cant manually change i for some reason? so im using a counter x instead
            match = total_list[i].startswith(to_find) if not full_line_check else total_list[x] == to_find
            if match:  # if current line is the one to add under / replace
                if save_to == -1 or allow_multiple_matches:  # if -1 then first match
                    save_to = set_save_to(save_to, i + 1)  # set save_to to the save index
                else:
                    msg = "ERROR: Multiple matches found"
                    await channel.send(msg)
                    log_message(msg)
                    return

        if save_to == -1:
            msg = "ERROR: No matches found"
            await channel.send(msg)
            log_message(msg)
            return

        if remove_or_replace:
            if to_add == "":
                if isinstance(save_to, int):
                    total_list.pop(save_to - 1)
                elif isinstance(save_to, list):
                    for ind in save_to:
                        total_list.pop(ind - 1)
                        for i in range(len(save_to)):
                            save_to[i] -= 1
            else:
                if isinstance(save_to, int):
                    total_list[save_to - 1] = to_add
                elif isinstance(save_to, list):
                    for ind in save_to:
                        total_list[ind - 1] = to_add
                        for i in range(len(save_to)):
                            save_to[i] -= 1
        else:
            if isinstance(save_to, int):
                if add_above:
                    total_list.insert(save_to - 1, to_add)
                else:
                    total_list.insert(save_to, to_add)
            elif isinstance(save_to, list):
                for ind in save_to:
                    if add_above:
                        total_list.insert(ind - 1, to_add)
                    else:
                        total_list.insert(ind, to_add)
                    for i in range(len(save_to)):
                        save_to[i] += 1

    else:
        if not index_to_add == -1:  # if insert at custom number
            total_list.insert(index_to_add, to_add)
        elif not index_to_change == -1:
            if to_add == "":
                total_list.pop(index_to_change - 1)
            else:
                total_list[index_to_change - 1] = to_add
        elif not replace_all:  # otherwise add to end
            total_list.append(to_add)

    new_msg = "\n".join(total_list)
    new_msg = new_msg.replace(to_find, to_add) if replace_all else new_msg
    if len(new_msg) > MESSAGE_LENGTH:
        await message_over_limit(new_msg, channel)
    else:
        await channel.send(new_msg)

    await delete_messages(bot_messages)  # Delete previous list messages
    if not isinstance(channel, discord.TextChannel):
        await channel.message.delete()  # Delete the command message if ctx is passed


async def delete_messages(messages):
    for i in messages:
        await i.delete()


async def find_all_bot_messages(ctx: discord.TextChannel, clear_what: str = "list"):
    mine = []
    async for x in ctx.history():
        match_text = not x.content.startswith("ERROR: ") and not x.content.startswith(
            "**__ListBot Help Menu") and not x.content.startswith("LIST LINE COUNT: ") and not x.content.startswith(
            "**Replaceable text found in the following channels:**") and not x.content.startswith("**Beginning search")
        match_author = x.author == bot.user
        match = False

        if clear_what == "list" and match_text and match_author:
            match = True
        elif clear_what == "status" and not match_text and match_author:
            match = True
        elif clear_what == "all" and match_author:
            match = True

        if match:
            mine.append(x)
    return mine[::-1]


def get_lines_in_list(my_messages):
    num_lines = 0  # number of lines in the list
    for x in my_messages:
        num_lines += len(x.content.split("\n"))

    return num_lines


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("ERROR: Invalid number of arguments. For more information, see `+help`.")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send("ERROR: Bad Argument. Make sure to follow the argument structure outlined in `+help`.")


@bot.command()
async def help(ctx):
    log(ctx.channel, ctx.channel.category, 'help', ctx.author)
    await ctx.send("""**__ListBot Help Menu P1:__**
To trigger any ListBot commands, begin your message with the `+` symbol
  
NOTE: To use any multi-word arguments, they MUST be wrapped in ". To use `"` inside an argument, put a `\` backslash before it, ie `\\"`
  
**Commands:**
`add ARGUMENT1`: Adds `ARGUMENT1` to the end of this channel's list. If there is no list, it will create a new one. Adding a second argument will specify what line it should be added under (by default will only accept 1 match, looking at the beginning of line).
  Further arguments can be added, as listed here:
    `-full` or `-f`: Matches will only respond to full lines
    `-above` or `-aa`: The line will be added above the match instead of below
    `-all`: The line will be added under all matches
`addundernum NUM ARGUMENT`: Adds `ARGUMENT` under line #`NUM`.
`getnumlines`: Replies with the number of lines in the list
`remove ARGUMENT1`: Removes the line beginning with `ARGUMENT1`. Will only remove one line, and fails if more than one line matches the specified `ARGUMENT1`. Adding "true" as a second argument will only match with full line matches.
  Further arguments can be added, as listed here:
    `-full` or `-f`: Matches will only respond to full lines
    `-all` or `-a`: All matches will be removed
`clear`: Clears this channel's list.
  Further arguments can be added to specify clear details:
    `-status` or `-s`: Delete status messages (help menu, errors, etc)
    `-all` or `-a`: Delete all ListBot messages.
`removenum NUM`: Removes the line at the specified number
`removewhite`: Removes empty lines
`replace ARGUMENT1 ARGUMENT2`: Replaces `ARGUMENT1` with `ARGUMENT2`. `ARGUMENT1` matches for the beginning of a line, and the command fails if there are multiple matches. Accepts full line specification
  Further arguments can be added, as listed here:
    `-full` or `-f`: Matches will only respond to full lines
    `-all` or `-a`: All matches will be removed"""
                   )
    await ctx.send("""**__ListBot Help Menu P2:__**
`replaceallincategory ARGUMENT1 ARGUMENT2`: Runs a `replaceall` in every channel in the current category, and summarizes which ones found a match. WARNING: Can get spammy
`replacenum NUM ARG1`: Replaces the line at the specified number with the given `ARG1`
`dm`: DMs the user the list
  `-raw` or `-r`: Escapes markdown characters. List of characters that are escaped is (`\, _, *, ~, :, |, ", >, -`, \`)
`effect` ARG1 OPTIONS: Applies an effect to the supplied text. See below for options.
  `-bold` or `-b`: Surrounds the text with \*\*, making it bold.
  `-italic` or `-i`: Surrounds the text with \_, making it italic.
  `-underline` or `-u`: Surrounds the text with \_\_, making it underlined.
  `-kill` or `-k`: Surrounds the text with \~\~, making it struckthrough.
  The order the options are applied is the order they're listed; e.g., using all four at once results in `~~___**text**___~~`.
"""
                   )


@bot.command()
async def add(ctx, arg1, *args):
    log(ctx.channel, ctx.channel.category, 'add', ctx.author, [arg1, *args])
    keywords = ["-full", "-f", "-above", "-aa", "-all"]
    key = False
    to_find = ""
    if args:
        for k in keywords:
            if k == args[0]:
                key = True
                break
        to_find = args[0] if not key else ""
    match_full = "-full" in args or "-f" in args
    add_above = "-above" in args or "-aa" in args
    allow_multiple = "-all" in args
    await send_list(ctx, await find_all_bot_messages(ctx.channel), to_add=arg1, to_find=to_find,
                    full_line_check=match_full, add_above=add_above, allow_multiple_matches=allow_multiple)


@bot.command()
async def remove(ctx, arg1, *args):
    log(ctx.channel, ctx.channel.category, 'remove', ctx.author, [arg1, *args])
    match_full = "-full" in args or "-f" in args
    allow_multiple = "-all" in args or "-a" in args
    await send_list(ctx, await find_all_bot_messages(ctx.channel), to_find=arg1, remove_or_replace=True,
                    full_line_check=match_full, allow_multiple_matches=allow_multiple)


@bot.command()
async def clear(ctx, arg1: str = "list"):
    log(ctx.channel, ctx.channel.category, 'clear', ctx.author, [arg1])
    arg1 = arg1.lower()
    if arg1 == "-status" or arg1 == "-s":
        arg1 = "status"
    if arg1 == "-all" or arg1 == "-a":
        arg1 = "all"
    await delete_messages(await find_all_bot_messages(ctx.channel, clear_what=arg1))


@bot.command()
async def removewhite(ctx):
    log(ctx.channel, ctx.channel.category, 'removewhite', ctx.author)
    await send_list(ctx, await find_all_bot_messages(ctx.channel), to_find="", full_line_check=True,
                    allow_multiple_matches=True, remove_or_replace=True)


@bot.command()
async def replace(ctx, arg1, arg2, *args):
    log(ctx.channel, ctx.channel.category, 'replace', ctx.author, [arg1, arg2, *args])
    match_full = "-full" in args or "-f" in args
    allow_multiple = "-all" in args or "-a" in args
    await send_list(ctx, await find_all_bot_messages(ctx.channel), to_add=arg2, to_find=arg1, remove_or_replace=True,
                    full_line_check=match_full, replace_all=allow_multiple)


@bot.command()
async def effect(ctx, arg1, *args):
    log(ctx.channel, ctx.channel.category, 'effect', ctx.author, [arg1, *args])
    bold = '-bold' in args or '-b' in args
    italic = '-italic' in args or '-i' in args
    underline = '-underline' in args or '-u' in args
    kill = '-kill' in args or '-k' in args

    result = arg1

    if bold:
        result = f"**{result}**"
    if italic:
        result = f"_{result}_"
    if underline:
        result = f"__{result}__"
    if kill:
        result = f"~~{result}~~"
    await send_list(ctx, await find_all_bot_messages(ctx.channel), to_add=result, to_find=arg1, remove_or_replace=True,
                    replace_all=True)


@bot.command()
async def replacenum(ctx, arg1: int, arg2):
    log(ctx.channel, ctx.channel.category, 'replacenum', ctx.author, [arg1, arg2])
    my_messages = await find_all_bot_messages(ctx.channel)
    num_lines = get_lines_in_list(my_messages)

    if arg1 > num_lines:
        msg = "ERROR: Line specified is longer than total number of lines in list. Number of lines in list: " + str(
            num_lines)
        log_message(msg)
        await ctx.send(msg)
        return

    await send_list(ctx, my_messages, to_add=arg2, index_to_change=arg1)


@bot.command()
async def dm(ctx, *args):
    log(ctx.channel, ctx.channel.category, 'dm', ctx.author, args)
    my_messages = await find_all_bot_messages(ctx.channel)
    raw = "-raw" in args or '-r' in args
    if not raw:
        for x in my_messages:
            await ctx.author.send(x.content)
    else:
        for x in my_messages:
            to_send = x.content.replace("\\", "\\\\").replace("_", "\_").replace("*", "\*").replace("~", "\~").replace(
                "`", "\`").replace(":", "\:").replace("|", "\|").replace('"', '\\\\"').replace('\n>', '\n\>').replace('-', '\-')
            if to_send.startswith(">"):
                to_send = '\\' + to_send
            # Not technically required, but it's faster to perform an if statement then run the function for no reason
            if len(to_send) > MESSAGE_LENGTH:
                await message_over_limit(to_send, ctx.author)
            else:
                await ctx.author.send(to_send)


@bot.command()
async def removenum(ctx, arg1: int):
    log(ctx.channel, ctx.channel.category, 'removenum', ctx.author, [arg1])
    await replacenum(ctx, arg1, "")


@bot.command()
async def addundernum(ctx, arg1: int, arg2):
    log(ctx.channel, ctx.channel.category, 'addundernum', ctx.author, [arg1, arg2])
    my_messages = await find_all_bot_messages(ctx.channel)
    num_lines = get_lines_in_list(my_messages)

    if arg1 > num_lines:
        msg = "ERROR: Line specified is longer than total number of lines in list. Number of lines in list: " + str(
            num_lines)
        log_message(msg)
        await ctx.send(msg)
        return
    elif arg1 < 1:
        msg = "ERROR: Line specified is too low"
        log_message(msg)
        await ctx.send(msg)
        return

    await send_list(ctx, my_messages, to_add=arg2, index_to_add=arg1)


@bot.command()
async def addabovenum(ctx, arg1: int, arg2):
    log(ctx.channel, ctx.channel.category, 'addabovenum', ctx.author, [arg1, arg2])
    await addundernum(ctx, arg1 - 1, arg2)


@bot.command()
async def getnumlines(ctx):
    log(ctx.channel, ctx.channel.category, 'getnumlines', ctx.author)
    await ctx.send("LIST LINE COUNT: " + str(get_lines_in_list(await find_all_bot_messages(ctx.channel))))


@bot.command()
async def replaceall(ctx, arg1, arg2=""):
    log(ctx.channel, ctx.channel.category, 'replaceall', ctx.author, [arg1, arg2])
    await send_list(ctx, await find_all_bot_messages(ctx.channel), to_add=arg2, to_find=arg1, replace_all=True)


@bot.command()
async def replaceallincategory(ctx, arg1, arg2):
    log(ctx.channel, ctx.channel.category, 'replaceallincategory', ctx.author, [arg1, arg2])
    await ctx.send("**Beginning search...**")
    category = ctx.channel.category
    if not isinstance(category, discord.CategoryChannel):  # if not in a category
        msg = "ERROR: This text channel is not in a category"
        log_message(msg)
        await ctx.send(msg)
        return

    super_present = False
    channels = []
    not_channels = []

    for x in category.channels:
        my_messages = await find_all_bot_messages(x)
        test_string = "\n".join(i.content for i in my_messages)
        if arg1 in test_string:
            await send_list(x, my_messages, to_add=arg2, to_find=arg1, remove_or_replace=True, replace_all=True)
            channels.append("<#" + str(x.id) + ">")
            super_present = True
        else:
            not_channels.append("<#" + str(x.id) + ">")

    if not super_present:
        msg = "ERROR: No replaceable text (" + arg1 + ") found in any channel in this category"
        log_message(msg)
        await ctx.send(msg)
    else:
        output = "**Replaceable text found in the following channels:**\n" + "\n".join(
            channels) + "\n\n**Replaceable text not found in the following channels:**\n" + "\n".join(not_channels)
        if len(output) > MESSAGE_LENGTH:
            await message_over_limit(output, ctx.channel)
        else:
            await ctx.send(output)


@bot.command()
async def copyto(ctx, arg1):
    log(ctx.channel, ctx.channel.category, 'copyto', ctx.author, [arg1])
    msg = "ERROR: Invalid channel ID."
    try:
        arg1 = int(arg1)
    except ValueError:
        log_message(msg)
        await ctx.send(msg)
        return

    channel = bot.get_channel(arg1)
    if channel is None:
        log_message(msg)
        await ctx.send(msg)
    else:
        await send_list(channel, await find_all_bot_messages(ctx))


bot.run(TOKEN)
