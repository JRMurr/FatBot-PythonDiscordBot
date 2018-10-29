# pythonDiscordBot

This is a bot for discord using discord.py https://github.com/Rapptz/discord.py

It supports aliases, Imgur, youtube, and basic Twitch support.

Imgur and youtube needs to be oauthed which requires API keys and user authorization. To do so the
bot has to be run in a terminal to get those setup.

# Installing dependencies
1. Use `virtualenv` to set up a virtual environment (optional)
    1. `pip install virtualenv`
    2. `virtualenv -p python3 venv` #venv can be replaced with whatever you want the virtualenv directory to be called
    3. `source venv/bin/activate` # Activate the virtual environment. You'll need to do this every time you change shell sessions.
2. `pip install -r requirements.txt`
    * If you're not using a virtual environment, you'll probably want to add the `--user` flag so the packages aren't installed at the system level.
### Bot setup
Make sure this as all done in Python 3! So replace pip with pip3 and python with python3 probably.
1. Set up your `config.json`. You can look at `config-example.json` for reference
    1. Copy your Discord bot token into the `"discord_id"` field (you can find/make a bot [here](https://discordapp.com/developers/applications/))
    2. Copy in any other access tokens you may need
2. Install docker and docker-compose (Google it)
3. Run `docker-compose up`

### Running pylint
To run pylint on the entire project, you can run `pylint main cogs` or `pylint <file_name>.py` to lint a single file.
