# pythonDiscordBot

This is a bot for discord using discord.py https://github.com/Rapptz/discord.py

It supports aliases, imgur, youtube, and basic Twitch support.

Imgur and youtube needs to be oauthed which requires API keys and user authorization. To do so the
bot has to be run in a terminal to get those setup.

### Bot setup
Make sure this as all done in Python 3! So replace pip with pip3 and python with python3 probably.
1. Set up your `config.json`. You can look at `config-example.json` for reference
    1. Copy your Discord bot token into the `"discord_id"` field (you can find/make a bot [here](https://discordapp.com/developers/applications/))
    2. Copy in any other access tokens you may need
2. Install docker and docker-compose (Google it)
3. Run `docker-compose up`
