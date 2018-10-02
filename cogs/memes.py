from discord.ext import commands
import emoji


class memeCog:
    """dumb meme commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme_text(self, *args):
        # print(str(args))
        msg = ""
        if len(args) < 1:
            await self.bot.say("enter some text that will enter the lands of memes")
            return
        for word in args:
            for char in word:
                if char not in emoji.UNICODE_EMOJI:
                    msg += chr(0xFEE0 + ord(char))
                else:
                    msg += char
            msg += "  "
        await self.bot.say(msg)


def setup(bot):
    bot.add_cog(memeCog(bot))
