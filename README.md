# pythonDiscordBot

This is a bot for discord using discord.py https://github.com/Rapptz/discord.py

It supports aliases, imgur, youtube, and basic Twitch support. 

Imgur and youtube needs to be oauthed which requires API keys and user authorization. To do so the 
bot has to be run in a terminal to get those setup.

### Bot setup
Make sure this as all done in Python 3! So replace pip with pip3 and python with python3 probably.
1. Install requirements with `pip install -r requirements.txt`
2. Copy your discord API into config.json, in the field "discord_id".
3. Run the bot with `python main.py`