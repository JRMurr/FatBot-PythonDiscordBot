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
    'cogs.twitch'
]

description = '''the greatest bot in the world'''
cmdPrefix = '!'
bot = commands.Bot(command_prefix=cmdPrefix, description=description)
#client = discord.Client()



aliasfile = open('alias.json')
aliasDict = json.load(aliasfile)

quotefile = open('quotes.json')
quotes = json.load(quotefile)
#aliasDict = {}

respondToOwner = True
ownerResponses = ['Can do daddy','Sure thing pops','Anything for you dad','Right away father','Yes sir','Fine']

try:
    keyWords = json.load(open('keyWords.json'))
except Exception as e:
    keyWords = {}

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(
                extension, type(e).__name__, e))


@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices: str):
    """Chooses between multiple choices."""
    print('choose')
    await bot.say(random.choice(choices))


@bot.command(pass_context=True)
@checks.admin_or_permissions(manage_roles=True)
async def alias(ctx):
    """Creates a alias command

        ex: !alias sayHi say hi"""
    print("makeing alias")
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


@bot.command()
async def say(*args):
    msg = ' '.join(args)
    await bot.say(msg)


@bot.command()
async def quote():
    await bot.say(random.choice(quotes))


# *args would not give ' " ' character for some reason
@bot.command(pass_context=True)
async def savequote(ctx):
    args = ctx.message.content.split(' ')
    msg = ' '.join(args[1::])
    # if not msg.startswith('"'):
    #     await bot.say("first character of quote must be a ' \" ' ")
    #     return
    # tmp = msg[1::]
    # if tmp.find('"') == -1:
    #     await bot.say("needs a second '\"' at the end of the quote")
    #     return
    # if tmp.find('-') == -1:
    #     await bot.say("put an author after the quote with a -")
    #     return
    regex = re.compile(r'".+" \- (\w+\s*)+')
    if regex.search(msg):
        quotes.append(msg)
        with open('quotes.json', 'w') as fp:
            json.dump(quotes, fp,indent=4)
        await bot.say("added quote:" + msg)
    else:
        await bot.say("Quotes must be of the form '\"Quote\" - Source'")


@bot.command()
@checks.admin_or_permissions(manage_roles=True)
async def showquotes():
    msg = " \n"
    i = 0
    for quote in quotes:
        msg = msg + '\n' + str(i) + ": " + quote
        i += 1
        if len(msg) >= 1500:
            await bot.whisper(msg)
            msg = "\n"
    # while len(msg) >=2000:
    #     sub_msg = msg[::2000]
    #     index = sub_msg.rfind('\n')
    #     print("index: " + str(index))
    #     sub_msg = sub_msg[::index]
    #     await bot.whisper(sub_msg)
    #     msg = msg[index+1::]
    await bot.whisper(msg)


@bot.command(no_pm=True)
@checks.admin_or_permissions(manage_roles=True)
async def removequote(index: int):
    """Removes the indexed quote from list of quotes

        Cant be used in pms"""
    if index < 0 or index > len(quotes):
        await bot.say("index passed is greater than the number of quotes or is negative")
    to_remove = quotes[index]
    del quotes[index]
    with open('quotes.json', 'w') as fp:
        json.dump(quotes, fp,indent=4)
    await bot.say("removed: " + to_remove)


@bot.command(hidden=True)
@checks.is_owner()
async def load(*, module: str):
    """Loads a module."""
    module = module.strip()
    try:
        bot.load_extension(module)
    except Exception as e:
        await bot.say('\U0001f52b')
        await bot.say('{}: {}'.format(type(e).__name__, e))
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




@bot.event
async def on_message(message):
    global respondToOwner

    if message.author == bot.user:
        return
    if respondToOwner and checks.is_owner_check(message)and message.content.startswith(cmdPrefix):
        await bot.send_message(message.channel,random.choice(ownerResponses))


    await bot.process_commands(message)

    if message.content.startswith(cmdPrefix):
        print("processing " + message.content)
        msg = copy.copy(message)
        alias = msg.content.split(' ')[0]
        # remove prefix
        alias = alias[len(cmdPrefix)::]
        if alias in aliasDict:
            msg.content = cmdPrefix + aliasDict[alias][0] + " " + aliasDict[alias][1]
            print("running alias: " + msg.content)
            await bot.process_commands(msg)
    elif message.content.lower() in keyWords:
        await bot.send_message(message.channel,keyWords[message.content.lower()])
    # if message.content.startswith('~test'):
    #     counter = 0
    #     tmp = await bot.send_message(message.channel, 'Calculating messages...')
    #     async for log in bot.logs_from(message.channel, limit=100):
    #         if log.author == message.author:
    #             counter += 1
    #
    #     await bot.edit_message(tmp, 'You have {} messages.'.format(counter))
    # elif message.content.startswith('!sleep'):
    #     await asyncio.sleep(5)
    #     await bot.send_message(message.channel, 'Done sleeping')
    # elif message.content.startswith('~workpls'):
    #     await bot.send_message(message.channel,'work you fucking bot')


bot.run('TOKEN')
