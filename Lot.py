import discord
from discord.ext import commands
import os
from datetime import datetime

MESSAGE_LENGTH = 1950

_intents = discord.Intents.default()
_intents.message_content = True
_intents.messages = True
bot = commands.Bot(command_prefix = "+", intents = _intents)
bot.remove_command("help")

TOKEN = os.environ["LotToken"]  # API token

LOG_FILE = "./Lot.log"

def log_message(message):
  try:
    file = open(LOG_FILE, 'a')
    file.write(f"\n{datetime.now()} | {message}")
  finally:
    if not file.closed: file.close()

def log(channel : str, category : str, command : str, author : str, arguments : list[str] = []):
  """ Log activity to the .log file """
  log_message(f"Command executed: {command} (Category: {category}) | Channel: {channel} | Arguments: {arguments} | Executed by: {author}")

#client = discord.Client()
@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))

async def msgOver2000(msg, channel):
  lines = msg.split("\n")
          
  while not lines == []:
    checkedLines = []
	
    while not lines == [] and len("\n".join(checkedLines) + "\n" + lines[0]) < MESSAGE_LENGTH:
      checkedLines.append(lines[0])
      lines.pop(0)
	  
    await channel.send("\n".join(checkedLines))

def set_saveTo(saveTo, val):
  if isinstance(saveTo, int):
    return val
  elif isinstance(saveTo, list):
    saveTo.append(val)
    return saveTo
  else: return -1

async def SendList(channel, botMessages, toAdd = "", toFind = "",
                   removeOrReplace : bool = False, fullLineCheck : bool = False, add_above : bool = False,
                   indexToAdd : int = -1, replaceAll : bool = False, indexToChange : int = -1, allow_multiple_matches : bool = False
                   ):
  totalList = []
  for i in botMessages:
    totalList.extend(i.content.split("\n"))
    
  if (toFind != "" and not replaceAll) or fullLineCheck:     # if toFind is not empty - ie add part way through
    saveTo = [] if allow_multiple_matches else -1 # default value of -1 or empty list - it can never be inserted to -1 in a msg
    x = -1                              # starts at -1 so that first value is 0
    for i in range(len(totalList)):            # for each line in list
      x += 1      # in python it seems you cant manually change i for some reason? so im using a counter x instead
      match = totalList[x].startswith(toFind) if not fullLineCheck else totalList[x] == toFind
      if match:                           # if current line is the one to add under / replace
        if saveTo == -1 or allow_multiple_matches:                # if -1 then first match
          saveTo = set_saveTo(saveTo, x + 1)      # set saveTo to the save index
        else:
          msg = "ERROR: Multiple matches found"
          await channel.send(msg)
          log_message(msg)
          return
    
    if saveTo == -1:
      msg = "ERROR: No matches found"
      await channel.send(msg)
      log_message(msg)
      return
      
    if removeOrReplace:
      if toAdd == "":
        if isinstance(saveTo, int): totalList.pop(saveTo - 1)
        elif isinstance(saveTo, list):
          for ind in saveTo:
            totalList.pop(ind - 1)
            for i in range(len(saveTo)): saveTo[i] -= 1
      else:
        if isinstance(saveTo, int): totalList[saveTo - 1] = toAdd
        elif isinstance(saveTo, list):
          for ind in saveTo:
            totalList[saveTo - 1] = toAdd
            for i in range(len(saveTo)): saveTo[i] -= 1
    else:
      if isinstance(saveTo, int):
        if add_above: totalList.insert(saveTo - 1, toAdd)
        else: totalList.insert(saveTo, toAdd)
      elif isinstance(saveTo, list):
        for ind in saveTo:
          if add_above: totalList.insert(ind - 1, toAdd)
          else: totalList.insert(ind, toAdd)
          for i in range(len(saveTo)): saveTo[i] += 1
      
  else:
    if not indexToAdd == -1:                  # if insert at custom number
      totalList.insert(indexToAdd, toAdd)
    elif not indexToChange == -1:
      if toAdd == "":
        totalList.pop(indexToChange - 1)
      else:
        totalList[indexToChange - 1] = toAdd
    elif not replaceAll:                                 # otherwise add to end
      totalList.append(toAdd)
  
  newMsg = "\n".join(totalList)
  newMsg = newMsg.replace(toFind, toAdd) if replaceAll else newMsg
  if len(newMsg) > MESSAGE_LENGTH:
    await msgOver2000(newMsg, channel)
  else:
    await channel.send(newMsg)
    
  await DeleteMsgs(botMessages)        # Delete previous list messages
  if not isinstance(channel, discord.TextChannel):
    await channel.message.delete()  # Delete the command message if ctx is passed

async def DeleteMsgs(messages):
  for i in messages:
	  await i.delete()
 
async def FindAllBotMessages(ctx : discord.TextChannel, clearWhat : str = "list"):
  mine = []
  async for x in ctx.history():
    matchText = not x.content.startswith("ERROR: ") and not x.content.startswith("**__ListBot Help Menu") and not x.content.startswith("LIST LINE COUNT: ") and not x.content.startswith("**Replaceable text found in the following channels:**")
    matchAuthor = x.author == bot.user
    match = False

    if clearWhat == "list" and matchText and matchAuthor:
      match = True
    elif clearWhat == "status" and not matchText and matchAuthor:
      match = True
    elif clearWhat == "all" and matchAuthor:
      match = True

    if match:
      mine.append(x)
  return mine[::-1]

def GetLinesInList(myMessages):
  numLines = 0              # number of lines in the list
  for x in myMessages:
    numLines += len(x.content.split("\n"))
  
  return numLines

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
`replacenum NUM, ARG1`: Replaces the line at the specified number with the given `ARG1`
`dm`: DMs the user the list
  `-raw` or `-r`: Escapes markdown characters. List of characters that are escaped is (`\, _, *, ~, :, |, ", >`, \`)
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
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toAdd = arg1, toFind = to_find, fullLineCheck = match_full, add_above = add_above, allow_multiple_matches = allow_multiple)

@bot.command()
async def remove(ctx, arg1, *args):
  log(ctx.channel, ctx.channel.category, ctx.channel.category, 'remove', ctx.author, [arg1, *args])
  match_full = "-full" in args or "-f" in args
  allow_multiple = "-all" in args or "-a" in args
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toFind = arg1, removeOrReplace = True, fullLineCheck = match_full, allow_multiple_matches = allow_multiple)

@bot.command()
async def clear(ctx, arg1 : str = "list"):
  log(ctx.channel, ctx.channel.category, 'clear', ctx.author, [arg1])
  arg1 = arg1.lower()
  if arg1 == "-status" or arg1 == "-s": arg1 = "status"
  if arg1 == "-all" or arg1 == "-a": arg1 = "all"
  await DeleteMsgs(await FindAllBotMessages(ctx.channel, clearWhat = arg1))

@bot.command()
async def removewhite(ctx):
  log(ctx.channel, ctx.channel.category, 'removewhite', ctx.author)
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toFind = "", fullLineCheck = True, allow_multiple_matches = True, removeOrReplace = True)
  
@bot.command()
async def replace(ctx, arg1, arg2, *args):
  log(ctx.channel, ctx.channel.category, 'replace', ctx.author, [arg1, arg2, *args])
  match_full = "-full" in args or "-f" in args
  allow_multiple = "-all" in args or "-a" in args
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toAdd = arg2, toFind = arg1, removeOrReplace = True, fullLineCheck = match_full, allow_multiple_matches = allow_multiple)

@bot.command()
async def replacenum(ctx, arg1 : int, arg2):
  log(ctx.channel, ctx.channel.category, 'replacenum', ctx.author, [arg1, arg2])
  myMessages = await FindAllBotMessages(ctx.channel)
  numLines = GetLinesInList(myMessages)

  if arg1 > numLines:
    msg = "ERROR: Line specified is longer than total number of lines in list. Number of lines in list: " + str(numLines)
    log_message(msg)
    await ctx.send(msg)
    return

  await SendList(ctx, myMessages, toAdd = arg2, indexToChange = arg1)

@bot.command()
async def dm(ctx, *args):
  log(ctx.channel, ctx.channel.category, 'dm', ctx.author, args)
  myMessages = await FindAllBotMessages(ctx.channel)
  raw = "-raw" in args or '-r' in args
  if not raw:
    for x in myMessages:
      await ctx.author.send(x.content)
  else:
    for x in myMessages:
      toSend = x.content.replace("\\", "\\\\").replace("_", "\_").replace("*", "\*").replace("~", "\~").replace("`", "\`").replace(":", "\:").replace("|", "\|").replace('"', '\\\\"').replace('\n>', '\n\>')
      if toSend.startswith(">"): toSend = '\\' + toSend
      if len(toSend) > MESSAGE_LENGTH: # Not technically required, but it's faster to perform an if statement then run the function for no reason
        await msgOver2000(toSend, ctx.author)
      else:
        await ctx.author.send(toSend)

@bot.command()
async def removenum(ctx, arg1 : int):
  log(ctx.channel, ctx.channel.category, 'removenum', ctx.author, [arg1])
  await replacenum(ctx, arg1, "")

@bot.command()
async def addundernum(ctx, arg1 : int, arg2):
  log(ctx.channel, ctx.channel.category, 'addundernum', ctx.author, [arg1, arg2])
  myMessages = await FindAllBotMessages(ctx.channel)
  numLines = GetLinesInList(myMessages)

  if arg1 > numLines:
    msg = "ERROR: Line specified is longer than total number of lines in list. Number of lines in list: " + str(numLines)
    log_message(msg)
    await ctx.send(msg)
    return
  elif arg1 < 1:
    msg = "ERROR: Line specified is too low"
    log_message(msg)
    await ctx.send(msg)
    return
  
  await SendList(ctx, myMessages, toAdd = arg2, indexToAdd = arg1)

@bot.command()
async def addabovenum(ctx, arg1 : int, arg2):
  log(ctx.channel, ctx.channel.category, 'addabovenum', ctx.author, [arg1, arg2])
  await addundernum(ctx, arg1 - 1, arg2)

@bot.command()
async def getnumlines(ctx):
  log(ctx.channel, ctx.channel.category, 'getnumlines', ctx.author)
  await ctx.send("LIST LINE COUNT: " + str(GetLinesInList(await FindAllBotMessages(ctx.channel))))

@bot.command()
async def replaceall(ctx, arg1, arg2 = ""):
  log(ctx.channel, ctx.channel.category, 'replaceall', ctx.author, [arg1, arg2])
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toAdd = arg2, toFind = arg1, replaceAll = True)

@bot.command()
async def replaceallincategory(ctx, arg1, arg2):
  log(ctx.channel, ctx.channel.category, 'replaceallincategory', ctx.author, [arg1, arg2])
  category = ctx.channel.category
  if not isinstance(category, discord.CategoryChannel):             # if not in a category
    msg = "ERROR: This text channel is not in a category"
    log_message(msg)
    await ctx.send(msg)
    return
  
  superPresent = False
  channels = []
  notChannels = []
  
  for x in category.channels:
    #print("Starting channel " + x.name)
    myMessages = await FindAllBotMessages(x)
    testStr = "\n".join(i.content for i in myMessages)
    if arg1 in testStr:
      await SendList(x, myMessages, toAdd = arg2, toFind = arg1, removeOrReplace = True, replaceAll = True)
      channels.append("<#" + str(x.id) + ">")
      superPresent = True
    else:
      notChannels.append("<#" + str(x.id) + ">")
  
  if not superPresent:
    msg = "ERROR: No replaceable text (" + arg1 + ") found in any channel in this category"
    log_message(msg)
    await ctx.send(msg)
  else:
    output = "**Replaceable text found in the following channels:**\n" + "\n".join(channels) + "\n\n**Replaceable text not found in the following channels:**\n" + "\n".join(notChannels)
    if len(output) > MESSAGE_LENGTH:
      await msgOver2000(output, ctx.channel)
    else:
      await ctx.send(output)

bot.run(TOKEN)