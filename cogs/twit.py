import discord
from discord.ext import commands
from .utils import checks
import twitter
import json
import random

configDict = json.load(open('config.json'))

api = twitter.Api(consumer_key=configDict['twitter_consumer_key'],
                  consumer_secret=configDict['twitter_consumer_secret'],
                  access_token_key=configDict['twitter_accsess_token'],
                  access_token_secret=configDict['twitter_accsess_secret'])

rt = False
replies = True
STATUS_LINK = "https://twitter.com/{}/status/{}"
BANNED_USER_ROLES = ['Bad Memer']

try:
    tweet_log = json.load(open('twit.json'))
except Exception as e:
    tweet_log = {}


class twitterCog:
    """Commands for twitter"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_tweet(self, user):
        try:
            tweets = api.GetUserTimeline(
                screen_name=user, include_rts=rt, exclude_replies=replies, count=200)
            if len(tweets) == 0:
                await self.bot.say("no tweets found")
                return
            tweet = random.choice(tweets)
            await self.bot.say(STATUS_LINK.format(user, tweet.id))
        except Exception as e:
            await self.bot.say("error while getting tweets")

    @commands.command(pass_context=True)
    async def send_tweet(self, ctx, *, text):
        if checks.is_role(ctx, BANNED_USER_ROLES):
            await self.bot.say("no memes for you")
            return
        msg = ctx.message
        cmdPrefix = self.bot.command_prefix
        # clean any @s discord might change to discord ids
        new_text = ctx.message.clean_content[len(cmdPrefix + 'send_tweet '):]
        try:
            tweet = api.PostUpdate(new_text)
            await self.bot.say(STATUS_LINK.format(tweet.user.screen_name, tweet.id) + " tweet sent by - " + msg.author.name)
        except Exception as e:
            await self.bot.say("error while posting tweet")


def setup(bot):
    bot.add_cog(twitterCog(bot))
