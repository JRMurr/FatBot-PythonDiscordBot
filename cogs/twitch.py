from discord.ext import commands
from .utils import checks
from urllib.request import urlopen
import json
try:
    streamers = json.load(open('streamers.json'))
except Exception as e:
    streamers = {}


def get_twitch_response(twitchName):
    url = "https://api.twitch.tv/kraken/streams/" + twitchName
    contents = urlopen(url)
    data = contents.read().decode("utf-8")
    return json.loads(data)


def isStreamOnline(twitchName):
    resp = get_twitch_response(twitchName)
    return resp['stream'] is not None


async def bot_test(bot):
    await bot.say('ayy')


async def checkStreams(bot):
    for streamer in streamers:
        #print("streamer: " + streamer + "active: " + str(streamers[streamer]['active']))
        if streamers[streamer]['active']:
            if isStreamOnline(streamer):
                await bot.say(streamer + " is online http://www.twitch.tv/" + streamer)


class twitchCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def is_stream_online(self, twitchName):
        """Returns if the stream is online"""
        if isStreamOnline(twitchName):
            await self.bot.say("stream online")
        else:
            await self.bot.say("stream not online")

    @commands.command(hidden=True)
    async def workpls(self):
        await bot_test(self.bot)

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def addstreamer(self, twitchName):
        if twitchName in streamers:
            streamers[twitchName]['active'] = True
        else:
            streamers.update({twitchName: {active: True}})
        with open('streamers.json', 'w') as fp:
            json.dump(streamers, fp)
        await self.bot.say("now checking for " + twitchName + " to go live")

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def removestreamer(self, twitchName):
        if twitchName in streamers:
            streamers[twitchName]['active'] = False
        with open('streamers.json', 'w') as fp:
            json.dump(streamers, fp)
        await self.bot.say("removed " + twitchName)

    @commands.command(no_pm=True)
    async def checkstreams(self):
        """Returns what streams are live in this channel"""
        await checkStreams(self.bot)


def setup(bot):
    bot.add_cog(twitchCog(bot))
