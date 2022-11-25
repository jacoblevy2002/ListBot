import discord
from discord.ext import commands
import os

MESSAGE_LENGTH = 1950

_intents = discord.Intents.default()
_intents.message_content = True
_intents.messages = True
bot = commands.Bot(command_prefix = "+", intents = _intents)
bot.remove_command("help")

TOKEN = os.environ["LotToken"]  # API token


#client = discord.Client()
@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))

async def msgOver2000(msg, channel):
  print("msgOver2000 Called")
  lines = msg.split("\n")
          
  while not lines == []:
    checkedLines = []
	
    while not lines == [] and len("\n".join(checkedLines) + "\n" + lines[0]) < MESSAGE_LENGTH:
      checkedLines.append(lines[0])
      lines.pop(0)
	  
    await channel.send("\n".join(checkedLines))

async def SendList(channel, botMessages, toAdd = "", toFind = "", removeOrReplace : bool = False, fullLineCheck : bool = False, removeAllMatches : bool = False, indexToAdd : int = -1, replaceAll : bool = False, indexToChange : int = -1):
  print("SendList called")
  totalList = []
  for i in botMessages:
    totalList.extend(i.content.split("\n"))
    
  if (toFind != "" and not replaceAll) or fullLineCheck:     # if toFind is not empty - ie add part way through
    saveTo = -1                         # default value of -1 - it can never be inserted to -1 in a msg
    x = -1                              # starts at -1 so that first value is 0
    for i in range(len(totalList)):            # for each line in list
      x += 1      # in python it seems you cant manually change i for some reason? so im using a counter x instead
      match = totalList[x].startswith(toFind) if not fullLineCheck else totalList[x] == toFind
      if match:                           # if current line is the one to add under / replace
        if removeAllMatches:              # whether or not to remove all matches found. Overrides everything else
          totalList.pop(x)
          x = x - 1
        elif saveTo == -1:                # if 0 then first match
          saveTo = x + 1                  # set saveTo to the save index
        else:
          await channel.send("ERROR: Multiple matches found")
          return
    
    if not removeAllMatches:      # if not removing all matches - ie if change specific line
      if saveTo == -1:
        await channel.send("ERROR: No matches found")
        return
      
      if removeOrReplace:
        if toAdd == "":
          totalList.pop(saveTo - 1)
        else:
          totalList[saveTo - 1] = toAdd
      else:
        totalList.insert(saveTo, toAdd)
      
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
  print("FindAllBotMessages called")
  mine = []
  #m = await ctx.history()
  #messages = m.flatten()
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
  print("Done looking")
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
  await ctx.send("**__ListBot Help Menu P1:__**\nTo trigger any ListBot commands, begin your message with the `+` symbol\n\nNOTE: To use any multi-word arguments, they MUST be wrapped in \". To use `\"` inside an argument, put a `\\` backslash before it, ie `\\\"`\n\n**Commands:**\n`add ARGUMENT1`: Adds `ARGUMENT1` to the end of this channel's list. If there is no list, it will create a new one. Adding a second argument will specify what line it should be added under (will only accept 1 match, looks at beginning of line). Adding \"true\" as a third argument will tell it to match with an entire line only.\n`addundernum NUM ARGUMENT`: Adds `ARGUMENT` under line #`NUM`.\n`getnumlines`: Replies with the number of lines in the list\n`remove ARGUMENT1`: Removes the line beginning with `ARGUMENT1`. Will only remove one line, and fails if more than one line matches the specified `ARGUMENT1`. Adding \"true\" as a second argument will only match with full line matches.\n`clear`: Clears this channel's list. Adding \"status\" as an argument will make it only delete status messages (help menu, errors, etc), and adding \"all\" as an argument will make it delete all ListBot messages in the channel.\n`removemore ARGUMENT`: Like remove, but deletes all matches. Accepts full line specification\n`removenum NUM`: Removes the line at the specified number\n`removewhite`: Removes empty lines\n`replace ARGUMENT1 ARGUMENT2`: Replaces `ARGUMENT1` with `ARGUMENT2`. `ARGUMENT1` matches for the beginning of a line, and the command fails if there are multiple matches. Accepts full line specification")
  await ctx.send("**__ListBot Help Menu P2:__**\n`replaceall ARGUMENT1 ARGUMENT2`: Replaces all matches of `ARGUMENT1` with `ARGUMENT2` in the list, without any checks. Think using `CTRL + F` to replace all\n`replaceallincategory ARGUMENT1 ARGUMENT2`: Runs a `replaceall` in every channel in the current category, and summarizes which ones found a match. WARNING: Can get spammy\n`replacenum NUM, ARG1`: Replaces the line at the specified number with the given `ARG1`\n`raw`: DMs user the raw list, escaping markdown (ie, \"**__Example__**\" would display as \*\*\*\_\_Example\_\_\*\*\*\")\n`dm`: DMs the user the list, leaving markdown intact")

@bot.command()
async def add(ctx, arg1, arg2 = "", arg3 : bool = False):
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toAdd = arg1, toFind = arg2, fullLineCheck = arg3)

@bot.command()
async def remove(ctx, arg1, arg2 : bool = False):
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toFind = arg1, removeOrReplace = True, fullLineCheck = arg2)

@bot.command()
async def clear(ctx, arg1 : str = "list"):
  arg1 = arg1.lower()
  await DeleteMsgs(await FindAllBotMessages(ctx.channel, clearWhat = arg1))

@bot.command()
async def removemore(ctx, arg1, arg2 : bool = False):
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toFind = arg1, removeAllMatches = True, fullLineCheck = arg2)

@bot.command()
async def removewhite(ctx):
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toFind = "", fullLineCheck = True, removeAllMatches = True)
  
@bot.command()
async def replace(ctx, arg1, arg2, arg3 : bool = False):
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toAdd = arg2, toFind = arg1, removeOrReplace = True, fullLineCheck = arg3)

@bot.command()
async def replacenum(ctx, arg1 : int, arg2):
  myMessages = await FindAllBotMessages(ctx.channel)
  numLines = GetLinesInList(myMessages)

  if arg1 > numLines:
    await ctx.send("ERROR: Line specified is longer than total number of lines in list. Number of lines in list: " + str(numLines))
    return

  await SendList(ctx, myMessages, toAdd = arg2, indexToChange = arg1)

@bot.command()
async def dm(ctx):
  myMessages = await FindAllBotMessages(ctx.channel)
  for x in myMessages:
    await ctx.author.send(x.content)

@bot.command()
async def raw(ctx):
  myMessages = await FindAllBotMessages(ctx.channel)
  for x in myMessages:
    toSend = x.content.replace("\\", "\\\\").replace("_", "\_").replace("*", "\*").replace("~", "\~").replace("`", "\`").replace(":", "\:").replace("|", "\|").replace('"', '\\\\"')
    if len(toSend) > MESSAGE_LENGTH: # Not technically required, but it's faster to perform an if statement then run the function for no reason
      await msgOver2000(toSend, ctx.author)
    else:
      await ctx.author.send(toSend)

@bot.command()
async def removenum(ctx, arg1 : int):
  await replacenum(ctx, arg1, "")

@bot.command()
async def addundernum(ctx, arg1 : int, arg2):
  myMessages = await FindAllBotMessages(ctx.channel)
  numLines = GetLinesInList(myMessages)

  if arg1 > numLines:
    await ctx.send("ERROR: Line specified is longer than total number of lines in list. Number of lines in list: " + str(numLines))
    return
  elif arg1 < 1:
    await ctx.send("ERROR: Line specified is too low")
    return
  
  await SendList(ctx, myMessages, toAdd = arg2, indexToAdd = arg1)

@bot.command()
async def addabovenum(ctx, arg1 : int, arg2):
  await addundernum(ctx, arg1 - 1, arg2)

@bot.command()
async def getnumlines(ctx):
  await ctx.send("LIST LINE COUNT: " + str(GetLinesInList(await FindAllBotMessages(ctx.channel))))

@bot.command()
async def replaceall(ctx, arg1, arg2 = ""):
  await SendList(ctx, await FindAllBotMessages(ctx.channel), toAdd = arg2, toFind = arg1, replaceAll = True)

@bot.command()
async def replaceallincategory(ctx, arg1, arg2):
  category = ctx.channel.category
  if not isinstance(category, discord.CategoryChannel):             # if not in a category
    await ctx.send("ERROR: This text channel is not in a category")
    return
  
  superPresent = False
  channels = []
  notChannels = []
  
  for x in category.channels:
    print("Starting channel " + x.name)
    myMessages = await FindAllBotMessages(x)
    testStr = "\n".join(i.content for i in myMessages)
    if arg1 in testStr:
      await SendList(x, myMessages, toAdd = arg2, toFind = arg1, removeOrReplace = True, replaceAll = True)
      channels.append("<#" + str(x.id) + ">")
      superPresent = True
    else:
      notChannels.append("<#" + str(x.id) + ">")
  
  if not superPresent:
    await ctx.send("ERROR: No replaceable text (" + arg1 + ") found in any channel in this category")
  else:
    output = "**Replaceable text found in the following channels:**\n" + "\n".join(channels) + "\n\n**Replaceable text not found in the following channels:**\n" + "\n".join(notChannels)
    if len(output) > MESSAGE_LENGTH:
      await msgOver2000(output, ctx.channel)
    else:
      await ctx.send(output)

bot.run(TOKEN)