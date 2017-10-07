import discord
from discord.ext import commands
from cogs.utils import checks
import random
import copy
import json
import re
import asyncio  # for debug

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.CRITICAL)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

initial_extensions = [
    'cogs.imgur',
    'cogs.youtube',
    'cogs.twitch',
    'cogs.test',
    'cogs.twit',
    'cogs.memes',
    'cogs.quotes',
    'cogs.predict',
    'cogs.standings',
]
try:
    configDict = json.load(open('config.json'))
except Exception as e:
    configDict = {}

try:
    aliasDict = json.load(open('alias.json'))
except Exception as e:
    aliasDict = {}

description = '''the greatest bot in the world'''
cmdPrefix ="!"
if configDict['cmdPrefix']:
    cmdPrefix = configDict['cmdPrefix']
bot = commands.Bot(command_prefix=cmdPrefix, description=description)



respondToOwner = False
ownerResponses = ['Can do daddy','Sure thing pops','Anything for you dad','Right away father','Yes sir','Fine']

#channels where its ok to spam
try:
    whiteListedChannels = json.load(open('whitelist.json'))
except Exception as e:
    whiteListedChannels = []


try:
    keyWords = json.load(open('keyWords.json'))
except Exception as e:
    keyWords = {}

try:
    timeOutUsers = json.load(open('timeOutUsers.json'))
except Exception as e:
    timeOutUsers = {}


import linecache
import sys

def getExceptionString():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(discord.utils.oauth_url(bot.user.id,discord.Permissions.general()))
    print('------')

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            #print('Failed to load extension {}\n{}: {}'.format(
            #    extension, type(e).__name__, e))
            print("error loading " + extension + ","+getExceptionString())


@bot.command(hidden=True)
@checks.is_owner()
async def shutdown():
    await bot.say("shutting down")
    await bot.close()

@bot.command(pass_context=True)
@checks.admin_or_permissions(manage_roles=True)
#@checks.role_or_admin('Lord of Albums',manage_roles=True)
async def alias(ctx):

    """Creates a alias command

        ex: !alias sayHi say hi"""
    #print("makeing alias")
    args = ctx.message.content.split(' ')
    if len(args) <= 2:  # need alias, new name, and at least the 'real' command
        await bot.say("Usage: {0}alias <aliasname> <cmd with arguments>".format(cmdPrefix))
        return
    name = args[1]
    args = args[2::]  # remove alias and name from list
    #print("args: " + str(args))
    #print("name: " + name)
    if name in ctx.bot.commands or name is "help":
        await bot.say("dont overwrite big boi commands you goon")
    else:
        # make alias
        newCommand = []
        # index 0 is 'real' command
        # index 1 is the arguments for the command in a string
        newCommand.append(args[0])
        newCommand.append(' '.join(args[1::]))
        aliasDict.update({name: newCommand})
        with open('alias.json', 'w') as fp:
            json.dump(aliasDict, fp,indent=4)
        await bot.say("Created alias " + name)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices: str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))


@bot.command()
async def say(*args):
    msg = ' '.join(args)
    await bot.say(msg)

@bot.command(pass_context=True)
async def do_multiple(ctx,numTimes: int,*,command :str):
    """does the passed command the specifed number of times"""

    msg = copy.copy(ctx.message)
    msg.content = cmdPrefix + command
    if numTimes > 5:
        await bot.say("thats too many times boi chill")
        return
    if command.startswith("do_multiple"):
        await bot.say("u fukin thought")
        return
    for i in range(numTimes):
        await on_message(msg)


@bot.command(hidden=True)
@checks.is_owner()
async def load(*, module: str):
    """Loads a module."""
    module = module.strip()
    try:
        bot.load_extension(module)
    # except:
    #     await bot.say(getExceptionString())
    except Exception as e:
        await bot.say('\U0001f52b')
        #await bot.say('{}: {}'.format(type(e).__name__, e))
        await bot.say(getExceptionString())
    else:
        await bot.say('\U0001f44c')


@bot.command(hidden=True)
@checks.is_owner()
async def unload(*, module: str):
    """Unloads a module."""
    module = module.strip()
    try:
        bot.unload_extension(module)
    except Exception as e:
        await bot.say('\U0001f52b')
        await bot.say('{}: {}'.format(type(e).__name__, e))
    else:
        await bot.say('\U0001f44c')


@bot.command(hidden=True)
@checks.is_owner()
async def reload(*, module: str):
    """Loads a module."""
    module = module.strip()
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except Exception as e:
        await bot.say('\U0001f52b')
        await bot.say(getExceptionString())
    else:
        await bot.say('\U0001f44c')


@bot.command(pass_context=True, hidden=True)
async def get_id(ctx):
    await bot.say(ctx.message.author.id)


@bot.command(hidden=True)
@checks.is_owner()
async def testcheck():
    await bot.say("ayy")

# @bot.command(pass_context=True, hidden=True)
# async def do(ctx, times : int, *, command):
#     """Repeats a command a specified number of times."""
#     msg = copy.copy(ctx.message)
#     msg.content = command
#     for i in range(times):
#         await bot.process_commands(msg)
#
# @bot.command()

@bot.command(no_pm=True)
@checks.admin_or_permissions(manage_roles=True)
async def add_keyword(*args):
    """adds keyphrase/response to be checked

       paramaters should be add_keyword <string of words> : <response of words>
       notice the space before and after the ':'
       """
    if ':' not in args:
        await bot.say("input should be 'add_keyword <string of words> : <response of words>'\nmake sure there is a space before and after the ':'")
        return
    index = args.index(':')
    keyphrase = args[:index]
    response = args[index+1:]
    keyWords.update({(' '.join(keyphrase)).lower():' '.join(response)})
    with open('keyWords.json', 'w') as fp:
        json.dump(keyWords, fp,indent=4)
    await bot.say("added key '{}' with response '{}'".format((' '.join(keyphrase)).lower(),' '.join(response)))

@bot.command()
@checks.admin_or_permissions(manage_roles=True)
async def list_keywords():
    #print("keys:" + ','.join(keyWords.keys()))
    msg = "keys:"
    i = 0
    for key in keyWords.keys():
        #print("key:" + key)
        msg = msg + '\n' + str(i) + ": " + str(key)
        i += 1
        #print("msg:" + msg)
        if len(msg) >= 1500:
            await bot.whisper(msg)
            msg = "\n"
    await bot.whisper(msg)


@bot.command(no_pm=True)
@checks.admin_or_permissions(manage_roles=True)
async def remove_keyword(*args):
    """removes keyword phrase from keywords"""
    keyphrase = (' '.join(args)).lower()
    try:
        del keyWords[keyphrase]
    except KeyError as e:
        await bot.say("'{}' not in list of keywords".format(keyphrase))
    else:
        with open('keyWords.json', 'w') as fp:
            json.dump(keyWords, fp,indent=4)
        await bot.say("removed: " + keyphrase)



@bot.command()
@checks.is_owner()
async def toggle_owner_response():
   global respondToOwner
   respondToOwner = not respondToOwner



@bot.command(pass_context=True)
@checks.admin_or_permissions(manage_roles=True)
async def channel_whitelist(ctx,isWhitelist: bool):
    channel = ctx.message.channel
    #print("poo")
    if not isWhitelist and channel in whiteListedChannels:
        whiteListedChannels.remove(channel.id)
        await bot.say("removed channel from whitelist")
    elif isWhitelist and channel not in whiteListedChannels:
        whiteListedChannels.append(channel.id)
        await bot.say("added channel to whitelist")
    with open('whitelist.json', 'w') as fp:
                    json.dump(whiteListedChannels, fp,indent=4)

@bot.group(pass_context=True)
@checks.admin_or_permissions(kick_members=True)
async def timeout(ctx):
    """Timeout command group"""
    if ctx.invoked_subcommand is None:
        await bot.say("use {}help timeout".format(bot.command_prefix))



@timeout.command(pass_context=True)
@checks.admin_or_permissions(kick_members=True)
async def set_length(ctx,timeOutLength: int):
    """Usage: timeout set_length <length in min> <@mention of user(s) to timeout>

        When a user is in timeout, their current messages will stay but all new
        messages during the timeout will be deleted.
        (There may be a delay when the server is under a high load)
    """
    message = ctx.message
    for user in message.mentions:
        #save the end of the timeout
        timeOutUsers[user] = message.timestamp + datetime.timedelta(minutes = timeOutLength)
    await bot.say("{}".format(timeOutUsers))


# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

@bot.command()
async def alias_list():
    msg = ""
    for chunk in list(chunks(sorted(list(aliasDict.keys())),3)):
        length = len(chunk)
        if length == 3:
            msg+= "{} {} {}\n".format(chunk[0].ljust(20),chunk[1].ljust(20),chunk[2].ljust(20))
        elif length == 2:
            msg+= "{} {}\n".format(chunk[0].ljust(20),chunk[1].ljust(20))
        else:
            msg+= "{}\n".format(chunk[0].ljust(20))
        if len(msg) >= 1850:
            await bot.whisper("```"+msg +"```")
            msg = "\n"
    await bot.whisper("```"+msg +"```")


#key user id -> dict with timestamp of last message in a channel that cares, and timeout start timestamp
userLastCommand = {}

@bot.event
async def on_message(message):
    global respondToOwner
    #print(str(userLastCommand))
    deleteMessage = False
    workingMessage = copy.copy(message) #will use to make changes to the message so orignal message can still be used in func calls
    if message.author == bot.user:
        return
    if respondToOwner and checks.is_owner_check(message)and workingMessage.content.startswith(cmdPrefix):
        await bot.send_message(message.channel,random.choice(ownerResponses))

    # #delete if in timeout
    currentTime = message.timestamp
    # if message.author in timeOutUsers:
    #

    if workingMessage.content.lower().endswith("-del"):
	       deleteMessage = True
	       workingMessage.content = message.content[:-4].strip()

    if workingMessage.content.startswith(cmdPrefix):
        #print("processing " + message.content)
        botCommands = list(bot.commands.keys()) + list(aliasDict.keys())

        msg = copy.copy(workingMessage)
        passedCMD = msg.content.split(' ')[0]
        passedCMD = passedCMD[len(cmdPrefix)::]

        #check = lambda r: r.name == 'manage_roles'
        #role = discord.utils.find(check, message.author.roles)
        roles = message.author.permissions_in(message.channel)
        #print("roles {}".format(roles))
        if passedCMD in botCommands and message.channel.id not in whiteListedChannels and not roles.manage_channels:
            #command ran is an actual commands or alias

            if message.author in userLastCommand:
                timeStamps = userLastCommand[message.author]
                msg1 = timeStamps['msg1']
                msg2 = timeStamps['msg2']
                timeoutStart = timeStamps['timeoutStart']
                if timeoutStart is not None:
                    diff = currentTime - timeoutStart
                    if diff.total_seconds() < 30:
                        await bot.send_message(message.author, "You're in timeout, no memes for {:.1f} secs".format(30 - diff.total_seconds()))
                        return
                    else:
                        timeStamps.update({'timeoutStart':None})
                        userLastCommand.update({message.author:timeStamps})

                #msg1, msg2 stuff
                if msg1 is None:
                    #both will be none since msg2 will only have a time is msg1 is not none
                    msg1 = currentTime
                elif msg2 is None:
                    msg2 = currentTime
                elif (msg1 - msg2).total_seconds() > 0:
                    #msg1 is newer
                    msg2 = currentTime
                else:
                    msg1 = currentTime
                timeStamps.update({'msg1':msg1,'msg2':msg2})


                #check diff of msg1 and msg2 to see if they were sent in under 3 secs
                if msg1 is not None and msg2 is not None:
                    diff = abs(msg1 - msg2)
                    if diff.total_seconds() < 3:
                        timeStamps.update({'timeoutStart':currentTime})
                        userLastCommand.update({message.author:timeStamps})
            else:
                timeStamps = {"msg1":None,"msg2":None,"timeoutStart":None}
                userLastCommand.update({message.author:timeStamps})

        #'real' command
        await bot.process_commands(workingMessage)

        msg = copy.copy(workingMessage)
        alias = msg.content.split(' ')[0]
        # remove prefix
        alias = alias[len(cmdPrefix)::]
        if alias in aliasDict:
            msg.content = cmdPrefix + aliasDict[alias][0] + " " + aliasDict[alias][1]
            #print("running alias: " + msg.content)
            await bot.process_commands(msg)
    elif workingMessage.content.lower() in keyWords:
        await bot.send_message(message.channel,keyWords[message.content.lower()])
    if deleteMessage:
        await bot.delete_message(message)

bot.run(configDict['discord_id'])
