import discord
from discord.ext import commands
import pylast
import json
import asyncio


PERIOD_OVERALL = 'overall'
PERIOD_7DAYS = '7day'
PERIOD_1MONTH = '1month'
PERIOD_3MONTHS = '3month'
PERIOD_6MONTHS = '6month'
PERIOD_12MONTHS = '12month'
PERIODS =  [PERIOD_OVERALL, PERIOD_7DAYS, PERIOD_1MONTH, PERIOD_3MONTHS, PERIOD_6MONTHS, PERIOD_12MONTHS]
PERIOD_STR = ', '.join(PERIODS)
configDict = json.load(open('config.json'))

class lastFMCog:
    """Interacts with last FM"""
    
    def __init__(self, bot):
        self.bot = bot
        self.network = pylast.LastFMNetwork(api_key=configDict['last_fm_api_key'], api_secret=configDict['last_fm_secret'])
        self.user_cache = {}
    
    @commands.group(pass_context=True)
    async def lastfm(self,ctx):
        """Lastfm interactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("use {}help lastfm".format(self.bot.command_prefix))

    @lastfm.group(pass_context=True)
    async def top(self,ctx):
        if ctx.invoked_subcommand is None or ctx.invoked_subcommand.name is 'top':
            await self.bot.say("use {}help lastfm top".format(self.bot.command_prefix))
    
    async def get_user(self, ctx, username):
        if username in self.user_cache:
            return self.user_cache[username]
        user = self.network.get_user(username)
        try:
            user.get_country()
            self.user_cache[username] = user
            return user
        except:
            await self.bot.send_message(ctx.message.channel, "username {} not found".format(username)) ## syntax error for some reason
            return None

    async def print_top(self, ctx, topObj, isArtist=False):
        """Enumerates through a top object and prints them"""
        title_header = 'Artist' if isArtist else 'Title'
        msg = '{0: >4} {1: <48} {2: >3}\n'.format('Rank', title_header, 'Play count')
        for idx, item in enumerate(topObj):
            title = item.item.get_name() if isArtist else item.item.get_title()
            msg += "{2: >4}: {1: <50} {0.weight: >3}\n".format(item, title, idx+1)
            if len(msg) >= 1900:
                await self.bot.send_message(ctx.message.channel, "```{}```".format(msg))
                msg = ""
        if len(msg) > 0:
            await self.bot.send_message(ctx.message.channel, "```{}```".format(msg))

    @top.command(pass_context=True)
    async def albums(self,ctx, username, period=PERIOD_7DAYS, limit=10):
        """Returns a lastFM users top played albumns for the specified period
        
        valid periods are overall, 7day, 1month, 3month, 6month, 12month
        """
        if period not in PERIODS:
            await self.bot.say("invalid period, valid options are: " + PERIOD_STR)
            return 
        user = await self.get_user(ctx, username)
        if not user:
            return
        albums = user.get_top_albums(period, limit=limit)
        await self.print_top(ctx, albums)

    @top.command(pass_context=True)
    async def tracks(self,ctx, username, period=PERIOD_7DAYS, limit=10):
        """Returns a lastFM users top played tracks for the specified period
        
        valid periods are overall, 7day, 1month, 3month, 6month, 12month
        """
        if period not in PERIODS:
            await self.bot.say("invalid period, valid options are: " + PERIOD_STR)
            return 
        user = await self.get_user(ctx, username)
        if not user:
            return
        tracks = user.get_top_tracks(period, limit=limit)
        await self.print_top(ctx, tracks)
    
    @top.command(pass_context=True)
    async def artist(self,ctx, username, period=PERIOD_7DAYS, limit=10):
        """Returns a lastFM users top played artists for the specified period
        
        valid periods are overall, 7day, 1month, 3month, 6month, 12month
        """
        if period not in PERIODS:
            await self.bot.say("invalid period, valid options are: " + PERIOD_STR)
            return 
        user = await self.get_user(ctx, username)
        if not user:
            return
        artists = user.get_top_artists(period, limit=limit)
        await self.print_top(ctx, artists, True)

def setup(bot):
    bot.add_cog(lastFMCog(bot))



