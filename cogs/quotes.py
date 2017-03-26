from discord.ext import commands
from .utils import checks
import json
import random
import re

FILE_NAME = 'quotes.json'
INPUT_REGEX = re.compile(r'"(.+)" \- ((\S+\s*)+)')
OUTPUT_FORMAT = '"{}" - {}'  # Quote - source
LIST_FORMAT = "\n{} - "
MAX_WHISPER_LENGTH = 1500

# Load all quotes
try:
    quotes = json.load(open(FILE_NAME))
except Exception as e:
    print("Error loading quotes:\n{}".format(e))
    quotes = []


def setup(bot):
    bot.add_cog(quotesCog(bot))


def save_quotes():
    try:
        json.dump(quotes, open(FILE_NAME, 'w'), indent=4)
    except Exception as e:
        print("Error saving quotes")


def format_quote(quote):
    return OUTPUT_FORMAT.format(quote[0], quote[1])


class quotesCog:
    """Commands for quotes"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self, *args):
        if args:
            # Filter for a word
            target = ' '.join(args)  # Combine the given words with spaces
            filtered_quotes = [q for q in quotes if target.lower() in q.lower()]
            if len(filtered_quotes) > 0:
                selection = filtered_quotes
            else:
                selection = quotes
                await self.bot.say("No quotes with that word. I'm giving you random stuff instead.")
        await self.bot.say(format_quote(random.choice(selection)))

    # *args would not give ' " ' character for some reason
    @commands.command(pass_context=True)
    async def savequote(self, ctx):
        args = ctx.message.content.split(' ')
        msg = ' '.join(args[1:])
        match = INPUT_REGEX.match(msg)
        if match:
            quotes.append((match.group(1), match.group(2)))  # List of (quote, source)
            save_quotes()
            await self.bot.say("Added quote: " + msg)
        else:
            await self.bot.say("Quotes must be of the form '\"Quote\" - Source'")

    @commands.command()
    @checks.admin_or_permissions(manage_roles=True)
    async def showquotes(self):
        msg = " \n"
        for i in range(len(quotes)):
            msg += '\n' + OUTPUT_FORMAT.format(quotes[i][0], quotes[i][1])  # quote, source
            if len(msg) >= MAX_WHISPER_LENGTH:
                await self.bot.whisper(msg)
                msg = "\n"
        await self.bot.whisper(msg)

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def removequote(self, index: int):
        """Removes the indexed quote from list of quotes

            Cannot be used in PMs"""
        if 0 <= index < len(quotes):
            to_remove = quotes[index]
            del quotes[index]
            save_quotes()
            await self.bot.say("Removed: " + to_remove)
        else:
            await self.bot.say("Invalid index")
