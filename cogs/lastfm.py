import discord
from discord.ext import commands
import pylast
import json
import asyncio

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

PERIOD_OVERALL = 'overall'
PERIOD_7DAYS = '7day'
PERIOD_1MONTH = '1month'
PERIOD_3MONTHS = '3month'
PERIOD_6MONTHS = '6month'
PERIOD_12MONTHS = '12month'
PERIODS = [PERIOD_OVERALL, PERIOD_7DAYS, PERIOD_1MONTH,
           PERIOD_3MONTHS, PERIOD_6MONTHS, PERIOD_12MONTHS]
PERIOD_STR = ', '.join(PERIODS)
configDict = json.load(open('config.json'))
FONT_PATH = 'fonts/Butler_ExtraBold.otf'
FONT_SIZE = 14
IMG_SAVE_DIR = 'lastfm_images/'


class lastFMCog:
    """Interacts with last FM"""

    def __init__(self, bot):
        self.bot = bot
        self.network = pylast.LastFMNetwork(
            api_key=configDict['last_fm_api_key'], api_secret=configDict['last_fm_secret'])
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        self.user_cache = {}

    @commands.group(pass_context=True)
    async def lastfm(self, ctx):
        """Lastfm interactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("use {0}help lastfm\nFor grid run {0}lastfm user grid, for lists run {0}lastfm top".format(self.bot.command_prefix))

    @lastfm.group(pass_context=True)
    async def top(self, ctx):
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
            # syntax error for some reason
            await self.bot.send_message(ctx.message.channel, "username {} not found".format(username))
            return None

    async def print_top(self, ctx, topObj, isArtist=False):
        """Enumerates through a top object and prints them"""
        title_header = 'Artist' if isArtist else 'Title'
        msg = '{0: >4} {1: <48} {2: >3}\n'.format(
            'Rank', title_header, 'Play count')
        for idx, item in enumerate(topObj):
            title = item.item.get_name() if isArtist else item.item.get_title()
            msg += "{2: >4}: {1: <50} {0.weight: >3}\n".format(
                item, title, idx+1)
            if len(msg) >= 1900:
                await self.bot.send_message(ctx.message.channel, "```{}```".format(msg))
                msg = ""
        if len(msg) > 0:
            await self.bot.send_message(ctx.message.channel, "```{}```".format(msg))

    @top.command(pass_context=True)
    async def albums(self, ctx, username, period=PERIOD_7DAYS, limit=10):
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
    async def tracks(self, ctx, username, period=PERIOD_7DAYS, limit=10):
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
    async def artist(self, ctx, username, period=PERIOD_7DAYS, limit=10):
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

    @lastfm.group(pass_context=True)
    async def user(self, ctx):
        if ctx.invoked_subcommand is None or ctx.invoked_subcommand.name is 'user':
            await self.bot.say("use {}help lastfm user".format(self.bot.command_prefix))

    @user.command(pass_context=True)
    async def scrobble(self, ctx, username):
        """Gets the users current playng song if they are playing one"""
        user = await self.get_user(ctx, username)
        if not user:
            return
        track = user.get_now_playing()
        msg = '{} '.format(username)
        if track:
            msg += 'is currently scrobbling {0}, they have played this song {1} time(s)'.format(
                track, track.get_userplaycount())
        else:
            msg += 'is not scrobbling a song right now'
        await self.bot.say(msg)

    @user.command(pass_context=True)
    async def recent(self, ctx, username, limit=10):
        """Grabs the specified users recent scrobbled songs"""
        user = await self.get_user(ctx, username)
        if not user:
            return
        tracks = user.get_recent_tracks(limit=limit)
        msg_prefix = '{}\'s recent scrobbled tracks are: \n'.format(username)
        msg = ''
        for idx, track in enumerate(tracks):
            msg += '{0: >2}: {1}\n'.format(idx+1, track.track)
            if len(msg) > 1900:
                msg = '```{}```'.format(msg)
                if msg_prefix:
                    msg = msg_prefix + msg
                await self.bot.say(msg)
                msg = ''
        if len(msg) >= 0:
            msg = '```{}```'.format(msg)
            if msg_prefix:
                msg = msg_prefix + msg
            print(msg)
            await self.bot.say(msg)

    def get_image(self, url):
        if url is None or len(url) == 0:
            return Image.new('RGB', (300, 300))
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((300, 300))
        return img

    def image_text(self, img, text, x_pos=0, y_pos=0):
        """Adds text to the image at the specified location"""
        # Make blank image for text
        txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(txt)
        # offset with black text to fake outline
        d.text((x_pos+1, y_pos+1), text, font=self.font, fill=(0, 0, 0, 255))
        d.text((x_pos+1, y_pos), text, font=self.font, fill=(0, 0, 0, 255))
        d.text((x_pos, y_pos+1), text, font=self.font, fill=(0, 0, 0, 255))
        #text in white
        d.text((x_pos, y_pos), text, font=self.font, fill=(255, 255, 255, 255))
        out = Image.alpha_composite(img.convert("RGBA"), txt)
        return out

    @user.command(pass_context=True)
    async def grid(self, ctx, username, period=PERIOD_7DAYS):
        """Returns a lastFM users 9 most played albumns for the specified period in a grid image

        valid periods are overall, 7day, 1month, 3month, 6month, 12month
        """
        if period not in PERIODS:
            await self.bot.say("invalid period, valid options are: " + PERIOD_STR)
            return
        user = await self.get_user(ctx, username)
        if not user:
            return
        msg = await self.bot.say('Making grid for {}, this will take a few seconds'.format(username))
        GRID_SIZE = 3
        albumns = user.get_top_albums(period, limit=GRID_SIZE**2 + 1)
        new_im = Image.new('RGB', (GRID_SIZE * 300, GRID_SIZE * 300))
        for y_idx in range(0, GRID_SIZE):
            for x_idx in range(0, GRID_SIZE):
                album_idx = y_idx * 3 + x_idx
                album = albumns[album_idx].item
                try:
                    imgUrl = album.get_cover_image(size=4)
                except pylast.WSError:
                    print('caught thing')
                    imgUrl = None

                alb_image = self.get_image(imgUrl)
                text = "{}\n{}".format(
                    album.get_artist().get_name(), album.get_title())
                alb_image = self.image_text(alb_image, text)
                new_im.paste(alb_image, (x_idx*300, y_idx*300))
        img_path = '{}/{}_grid.jpg'.format(IMG_SAVE_DIR, username)
        new_im.save(img_path, format='JPEG')
        await self.bot.delete_message(msg)
        await self.bot.upload(img_path)


def setup(bot):
    bot.add_cog(lastFMCog(bot))
