from discord.ext import commands
from .utils import checks


class testCog:
    """Commands for testing things"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True)
    @checks.role_or_admin('Lord of Albums', manage_roles=True)
    async def test_role(self):
        await self.bot.say("\U0001f44c")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def get_roles(self, ctx):
        msg = "Roles:\n"
        for role in ctx.message.author.roles:
            msg = msg + "name: " + role.name + " id: " + \
                role.id + " pos: " + str(role.position) + "\n"
        msg.replace('@', '')
        await self.bot.say(msg)


def setup(bot):
    bot.add_cog(testCog(bot))
