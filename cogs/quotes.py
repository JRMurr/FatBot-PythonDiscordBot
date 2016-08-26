import discord
from discord.ext import commands
from .utils import checks
import json
import random
quotefile = open('quotes.json')
quotes = json.load(quotefile)

class quotesCog:
    """Commands for testing things"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self,*args):
        selection = quotes
        if len(args) > 0:
            filtered_quotes = [quote for quote in quotes if args[0].lower() in quote.lower()] # Filter for a word
            if len(filtered_quotes) > 0:
                selection = filtered_quotes
            else:
                await self.bot.say("No quotes with that word")
        await self.bot.say(random.choice(selection))

    # *args would not give ' " ' character for some reason
    @commands.command(pass_context=True)
    async def savequote(self,ctx):
        args = ctx.message.content.split(' ')
        msg = ' '.join(args[1::])
        # if not msg.startswith('"'):
        #     await self.bot.say("first character of quote must be a ' \" ' ")
        #     return
        # tmp = msg[1::]
        # if tmp.find('"') == -1:
        #     await self.bot.say("needs a second '\"' at the end of the quote")
        #     return
        # if tmp.find('-') == -1:
        #     await self.bot.say("put an author after the quote with a -")
        #     return
        regex = re.compile(r'".+" \- (\w+\s*)+')
        if regex.search(msg):
            quotes.append(msg)
            with open('quotes.json', 'w') as fp:
                json.dump(quotes, fp,indent=4)
            await self.bot.say("added quote:" + msg)
        else:
            await self.bot.say("Quotes must be of the form '\"Quote\" - Source'")


    @commands.command()
    @checks.admin_or_permissions(manage_roles=True)
    async def showquotes(self):
        msg = " \n"
        i = 0
        for quote in quotes:
            msg = msg + '\n' + str(i) + ": " + quote
            i += 1
            if len(msg) >= 1500:
                await self.bot.whisper(msg)
                msg = "\n"
        # while len(msg) >=2000:
        #     sub_msg = msg[::2000]
        #     index = sub_msg.rfind('\n')
        #     print("index: " + str(index))
        #     sub_msg = sub_msg[::index]
        #     await self.bot.whisper(sub_msg)
        #     msg = msg[index+1::]
        await self.bot.whisper(msg)


    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def removequote(self,index: int):
        """Removes the indexed quote from list of quotes

            Cant be used in pms"""
        if index < 0 or index > len(quotes):
            await self.bot.say("index passed is greater than the number of quotes or is negative")
        to_remove = quotes[index]
        del quotes[index]
        with open('quotes.json', 'w') as fp:
            json.dump(quotes, fp,indent=4)
        await self.bot.say("removed: " + to_remove)


def setup(bot):
    bot.add_cog(quotesCog(bot))
