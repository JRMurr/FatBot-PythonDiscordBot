from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from imgurpython.helpers.error import ImgurClientRateLimitError
from discord.ext import commands
from .utils import checks
import json
import random

from urllib.parse import urlparse
from os.path import splitext
from enum import Enum

configFile = open('config.json')
configDict = json.load(configFile)

imgurClient = ImgurClient(configDict['imgur_client_id'], configDict['imgur_client_secret'])
imgurClient.set_user_auth(configDict['imgur_access_token'], configDict['imgur_refresh_token'])


class linkType(Enum):
    album = 1
    imgurlink = 2
    other = 3


def makeAlbumFromAlbum(title, albumlink):
    albumName = title.lower()
    for album in imgurClient.get_account_albums('me'):
        if albumName == album.title.lower():
            print('aaaaa')
            # await self.bot.say(albumName + " is already an album")
            break
    else:
        data = urlparse(albumlink)
        oldAlbumID = data.path[3::]  # remove /a/
        oldImages = imgurClient.get_album_images(str(oldAlbumID))
        imageIDs = []
        for image in oldImages:
            imageIDs.append(image.id)
        fields = {'title': albumName, 'ids': ','.join(imageIDs)}
        imgurClient.create_album(fields)


def checkImgurUrl(link):
    data = urlparse(link)
    if 'imgur.com' not in data.netloc:
        return {'linkType': linkType.other, 'path': link}  # pass link as path since its not imgur
    elif data.path.startswith('/a/'):
        return {'linkType': linkType.album, 'path': data.path[3::]}  # remove the /a/
    else:
        path = data.path[1::]  # remove '/'
        if '.' in path:
            path = path[:path.index('.')]
        return {'linkType': linkType.imgurlink, 'path': path}


class imgurCog:
    """Commands for imgur"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def imgur(self, *args):
        """Grabs a random picture from imgur album name passed"""
        if len(args) < 1:
            msg = "albums: "
            for album in imgurClient.get_account_albums('me'):
                msg = msg + str(album.title) + ','
            await self.bot.say(msg)
            return

        albumName = args[0].lower()
        for album in imgurClient.get_account_albums('me'):
            #print("albumName: " + albumName + " title" + album.title)
            if albumName == album.title.lower():
                images = imgurClient.get_album_images(album.id)
                await self.bot.say(random.choice(images).link)
                break
        else:
            # album not found
            await self.bot.say("Album: " + albumName + " not found")

    @commands.command()
    @checks.role_or_admin('Lord of Albums', manage_roles=True)
    async def imgur_add(self, *args):
        """adds images to album, first parameter is albumName, rest are links"""
        if len(args) < 1:
            msg = "albums: "
            for album in imgurClient.get_account_albums('me'):
                msg = msg + album.title + ','
            await self.bot.say(msg)
            return
        elif len(args) == 1:
            await self.bot.say("pass a url to an image to add")
            return
        albumName = args[0].lower()
        for album in imgurClient.get_account_albums('me'):
            if albumName == album.title.lower():
                imageIDs = []
                numImages = 0
                for link in args[1:]:
                    returnDict = checkImgurUrl(link)
                    if returnDict['linkType'] is linkType.other:
                        try:
                            # await self.bot.say("uploading {}".format(returnDict['path']))
                            image = imgurClient.upload_from_url(
                                returnDict['path'], config=None, anon=True)
                            imageIDs.append(image['id'])
                        except ImgurClientError as e:
                            await self.bot.say("upload error: {} status: {}".format(e.error_message, e.status_code))
                        except ImgurClientRateLimitError:
                            await self.bot.say("Rate-limit exceeded")
                    elif returnDict['linkType'] is linkType.imgurlink:
                        # imgur just get id
                        imageIDs.append(returnDict['path'])
                        numImages += 1
                    else:
                        # album so add everything
                        oldImages = imgurClient.get_album_images(returnDict['path'])
                        for image in oldImages:
                            imageIDs.append(image.id)
                            numImages += 1
                imgurClient.album_add_images(album.id, ','.join(imageIDs))
                if len(imageIDs) == 0:
                    break
                await self.bot.say("added " + ','.join(imageIDs) + " to " + albumName)
                # await self.bot.say("added images to album")
                break
        else:
            # album not found
            await self.bot.say("Album: " + albumName + " not found.\nRun 'imgur_make_album' to create an album")

    @commands.command(no_pm=True)
    @checks.role_or_admin('Lord of Albums', manage_roles=True)
    async def imgur_make_album(self, title: str):
        """Creates empty album with specifed title"""
        albumName = title.lower()
        for album in imgurClient.get_account_albums('me'):
            if albumName == album.title.lower():
                await self.bot.say(albumName + " is already an album")
                break
        else:
            fields = {'title': albumName}
            imgurClient.create_album(fields)
            await self.bot.say("created album " + albumName)

    @commands.command(no_pm=True)
    @checks.role_or_admin('Lord of Albums', manage_roles=True)
    async def imgur_make_album_from_album(self, title: str, albumlink):
        """Creates empty album with specifed title from an already created album url"""
        albumName = title.lower()
        for album in imgurClient.get_account_albums('me'):
            if albumName == album.title.lower():
                await self.bot.say(albumName + " is already an album")
                break
        else:
            data = urlparse(albumlink)
            oldAlbumID = data.path[3::]  # remove /a/
            oldImages = imgurClient.get_album_images(str(oldAlbumID))
            imageIDs = []
            for image in oldImages:
                imageIDs.append(image.id)
            fields = {'title': albumName, 'ids': ','.join(imageIDs)}
            imgurClient.create_album(fields)
            await self.bot.say("created album " + albumName)

    @commands.command()
    @checks.role_or_admin('Lord of Albums', manage_roles=True)
    async def imgur_remove(self, albumName, imageLink):
        """removes image from album, pass direct image"""
        albumName = albumName.lower()
        for album in imgurClient.get_account_albums('me'):
            if albumName == album.title.lower():
                #image = imgurClient.upload_from_url(args[1], config=None, anon=True)
                # imgurClient.album_add_images(album.id,image['id'])
                images = imgurClient.get_album_images(album.id)
                # imageID = urlparse(imageLink).path[1::] #remove / at start
                imageID, ext = splitext(urlparse(imageLink).path)
                imageID = imageID[1::]
                for image in images:
                    if imageID == image.id:
                        imgurClient.album_remove_images(album.id, imageID)
                        await self.bot.say("removed {} from album".format(image.id))
                break
        else:
            # album not found
            await self.bot.say("Album: " + albumName + " not found")

    @commands.command()
    async def imgur_album(self, *args):
        """gives direct link to album"""
        if len(args) < 1:
            msg = "albums: "
            for album in imgurClient.get_account_albums('me'):
                msg = msg + album.title + ','
            await self.bot.say(msg)
            return

        albumName = args[0].lower()
        for album in imgurClient.get_account_albums('me'):
            if albumName == album.title.lower():
                await self.bot.say(album.link)
                break
        else:
            # album not found
            await self.bot.say("Album: " + albumName + " not found")


def setup(bot):
    bot.add_cog(imgurCog(bot))
