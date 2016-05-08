import discord
from discord.ext import commands
from .utils import checks
import random
from urllib.parse import urlparse
from urllib.parse import parse_qs

import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

args = argparser.parse_args()
youtube = get_authenticated_service(args)

def create_playlist(playlistName):
    try:
        playlists_insert_response = youtube.playlists().insert(
          part="snippet,status",
          body=dict(
            snippet=dict(
              title=playlistName
            ),
            status=dict(
                privacyStatus="public"
                )
            )
        ).execute()
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
    else:
        print("it worked")

def get_playlist(playlistName :str):
    results = youtube.playlists().list(
                part="snippet,player",
                mine=True,
                maxResults=50
    ).execute()
    playlists = results['items']
    for playlist in playlists:
        if playlist['snippet']['title'].lower() == playlistName.lower():
            return playlist
            break
    else:
        #playlist not found
        return None

def video_id(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


class youtubeCog:
    """Commands for youtube playlists"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def create_playlist(self,playlistName):
        """creates a playlist Admin only"""
        snippetDict = {'title':playlistName}
        statusDict = {'privacyStatus':"public"}
        bodyDict = {'snippet':snippetDict,'status':statusDict}
        try:
            playlists_insert_response = youtube.playlists().insert(
              part="snippet,status",
              body=bodyDict
            ).execute()
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            await self.bot.say("an error happend PANIC")
        else:
            await self.bot.say("created playlist " + playlistName)

    @commands.command()
    async def add_video(self,playlistName,videolink):
        """Adds the youtube video to the playlist passed"""
        videoID = video_id(videolink)
        if videoID is None:
            await self.bot.say("The link passed is not a valid youtube link")
            return
        print(str(type(playlistName)))
        playlist = get_playlist(playlistName)
        if playlist is None:
            await self.bot.say("Playlist not found")
            return
        playlistID = playlist['id']
        try:
            add_video_request=youtube.playlistItems().insert(
                part="snippet",
                body={"kind": "youtube#playlistItem",
                'snippet': {
                  'playlistId': playlistID,
                  'resourceId': {
                          'kind': 'youtube#video',
                          'videoId': videoID
                      }
                    }
                }
            ).execute()
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            await self.bot.say("an error happend PANIC")
        else:
            await self.bot.say("added " + videoID + " to " + playlistName)


    @commands.command()
    async def get_playlist(self,*args):
        """Returns a link to the playlist specified

        returns list of playlist if passed playlist is not found"""
        results = youtube.playlists().list(
                    part="snippet,player",
                    mine=True,
                    maxResults=50
        ).execute()
        playlists = results['items']
        if len(args) < 1:
            msg = "lists: "
            for playlist in playlists:
                msg = msg + playlist['snippet']['title'] + ","
            await self.bot.say(msg)
            return

        #check to see if playlist is in current list of playlists
        link = "https://www.youtube.com/playlist?list="
        for playlist in playlists:
            if playlist['snippet']['title'].lower() == args[0].lower():
                await self.bot.say("playlist " + args[0] + ": " + link + playlist['id'])

    @commands.command()
    async def getvid(self,playlistName :str):
        """Gets random video from playlist"""
        playlist = get_playlist(playlistName)
        if playlist is None:
            await self.bot.say("Playlist not found")
            return
        playlistID = playlist['id']
        playlist_items_resp = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlistID,
            maxResults=50
        ).execute()
        playlistItmes = playlist_items_resp['items']
        if(len(playlistItmes) <=0):
            await self.bot.say("no videos in playlist")
            return
        vid = random.choice(playlistItmes)
        link= 'https://www.youtube.com/watch?v='
        await self.bot.say("video: " + link + vid['contentDetails']['videoId'])

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remove_video(self,playlistName,videoNumber:int):
        """removes the specified video number(starts at 1) from the playlist. Admin only"""
        if videoNumber < 1:
            await self.bot.say("video number cant be less than 1")
            return
        playlist = get_playlist(playlistName)
        if playlist is None:
            await self.bot.say("Playlist not found")
            return
        playlistID = playlist['id']
        playlist_items_resp = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlistID,
            maxResults=50
        ).execute()
        playlistItmes = playlist_items_resp['items']
        if videoNumber > len(playlistItmes) :
            await self.bot.say("video number greater than number of videos in playlist")
            return
        to_remove = playlistItmes[videoNumber-1]
        del_resp = youtube.playlistItems().delete(id=to_remove['id']).execute()
        await self.bot.say("removed: " + to_remove['snippet']['title'])

def setup(bot):
    bot.add_cog(youtubeCog(bot))
