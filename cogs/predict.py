import discord
from discord.ext import commands
from .utils import checks
import json

# Gross code from aniion

#entries = {'Jack':['optic', 'gdsnt', 'tyloo', 'imt', 'c9', 'faze', 'g2', 'clg'],'Andy':['mouse', 'gdsnt', 'tyloo', 'imt', 'c9', 'faze', 'g2', 'clg']}
# teamfull 1st event = {'optic': 'OpTic Gaming', 'gdsnt': 'GODSENT', 'tyloo' : 'TyLoo', 'imt': 'Immortals', 'c9' : 'Cloud 9', 'faze': 'FaZe Clan', 'g2': 'G2 Esports', 'clg': 'Counter Logic Gaming', 'nip': 'Ninjas in Pyjamas', 'rng': 'Renegades', 'mouse' : 'mousesports', 'nv': 'Team EnVyUs', 'vega' : 'Vega Squadron', 'spirit': 'Team Spirit', 'dig' : 'Team Dignitas', 'hr' : 'HellRaisers'}
team_arr = ['SK Gaming', 'Liquid', 'Fnatic', 'Virtus.pro', 'Astralis', 'FlipSid3 Tactics', 'Gambit e-Sports',
            'Natus Vincere', 'FaZe Clan', 'GODSENT', 'mousesports', 'North', 'OpTic Gaming', 'EnVyUs', 'G2 Esports', 'HellRaisers']

try:
    predictJson = json.load(open('predict.json'))
except Exception as e:
    predictJson = {}


if 'teams' in predictJson:
    teams = predictJson['teams']
else:
    # set all teams as in
    # teams  1st event=  {'optic': 1, 'gdsnt': 1, 'tyloo': 1, 'imt': 1, 'c9': 1, 'faze': 1, 'g2': 1, 'clg': 1, 'nip': 1, 'rng': 1, 'mouse': 1, 'nv' : 1, 'vega': 1, 'dig' : 1, 'spirit': 1, 'hr': 1}
    teams = {}
    for team in team_arr:
        teams[team] = 1

if 'entries' in predictJson:
    entries = predictJson['entries']
else:
    entries = {}

if 'allowEntries' in predictJson:
    allowEntries = predictJson['allowEntries']
else:
    allowEntries = True


def returnfull(abbr):
    l = []
    for k in abbr:
        if teams[k] == 1:
            s = '**{}**'.format(k)
            l.append(s)
        else:
            l.append(k)
    return [x for x in l if x is not None]

# returns a dict with keys, 'valid', 'team', and 'error'


def team_name_autocomplete(name):
    possible_teams = []
    for team in teams:
        if team.lower().startswith(name.lower()):
            possible_teams.append(team)
    possible_len = len(possible_teams)
    returnDict = {'valid': False, 'team': None, 'error': None}
    if possible_len == 0:
        returnDict['error'] = 'No team starts with {}'.format(name)
    elif possible_len == 1:
        returnDict['valid'] = True
        returnDict['team'] = possible_teams[0]
    else:
        returnDict['error'] = 'Teams {}, all start with "{}", type more lazy ass'.format(
            ",".join(possible_teams), name)
    return returnDict


def total(d):
    sum = 0
    for key in d:
        sum += teams.get(key)
    return sum


class predictCog:
    """For predicting esport events"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def predict(self, ctx):
        """"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("use {}help predict".format(self.bot.command_prefix))

    @predict.command()
    async def teams(self):
        msg = ''
        for team in teams:
            msg += "{}\n".format(team)
        await self.bot.say(msg)

    @predict.command()
    @checks.role_or_admin('Bot Admin', manage_roles=True)
    async def disable_entries(self):
        allowEntries = False
        with open('predict.json', 'w') as fp:
            predictJson['allowEntries'] = allowEntries
            json.dump(predictJson, fp, indent=4)
        await self.bot.say("No longer taking entries")

    @predict.command()
    @checks.role_or_admin('Bot Admin', manage_roles=True)
    async def enable_entries(self):
        allowEntries = True
        with open('predict.json', 'w') as fp:
            predictJson['allowEntries'] = allowEntries
            json.dump(predictJson, fp, indent=4)
        await self.bot.say("Now takeing entries")

    @predict.command(pass_context=True)
    async def addentry(self, ctx, *args):
        """adds user predictions

        Usage: predict addentry <space seperate teams>
        Team name will autocomplete so for example you can enter "o" for optic or "fli" for FlipSid3
        If you need a space in a team name, put that team name in quotes
        """
        if not allowEntries:
            await self.bot.say("entries not allowed right now")
            return

        entry = []
        if len(args) != 8:
            await self.bot.say("specify 8 teams that you think will win")
            return
        for val in args:
            autoCompleteDict = team_name_autocomplete(val)
            if autoCompleteDict['valid']:
                entry.append(autoCompleteDict['team'])
            else:
                await self.bot.say(autoCompleteDict['error'])
                return
        entries[ctx.message.author.id] = entry
        with open('predict.json', 'w') as fp:
            predictJson['entries'] = entries
            json.dump(predictJson, fp, indent=4)
        await self.bot.say("added user {} with entry {}".format(ctx.message.author.name, entry))

    @predict.command()
    @checks.role_or_admin('Bot Admin', manage_roles=True)
    async def update(self, team):
        """sets the specifed team as out"""
        autoCompleteDict = team_name_autocomplete(team)
        if autoCompleteDict['valid']:
            teams[autoCompleteDict['team']] = 0
            with open('predict.json', 'w') as fp:
                predictJson['teams'] = teams
                json.dump(predictJson, fp, indent=4)
            await self.bot.say("{} is now out of the tournament".format(autoCompleteDict['team']))
        else:
            await self.bot.say(autoCompleteDict['error'])

    @predict.command()
    @checks.role_or_admin('Bot Admin', manage_roles=True)
    async def revert(self, team):
        """sets the specifed team as in (used when someone messed up)"""
        autoCompleteDict = team_name_autocomplete(team)
        if autoCompleteDict['valid']:
            teams[team] = 1
            with open('predict.json', 'w') as fp:
                predictJson['teams'] = teams
                json.dump(predictJson, fp, indent=4)
            await self.bot.say("somehow {} is back in the tournament".format(team))
        else:
            await self.bot.say(autoCompleteDict['error'])

    @predict.command(pass_context=True)
    async def display(self, ctx):
        """Displays the current standings of everyone's predictions"""
        s = ''
        for userId, arr in entries.items():
            name = discord.utils.find(lambda m: m.id == userId,
                                      ctx.message.channel.server.members).name
            s += '{} picked: '.format(name)
            s += ', '.join(returnfull(arr))
            s += ' -- %{}\n'.format((float(total(arr)) / 8) * 100)
            if len(s) > 1000:
                await self.bot.say(s)
                s = ''
        await self.bot.say(s)

    @predict.command(pass_context=True)
    async def ladder(self, ctx):
        ladder = {}
        for k, v in entries.items():
            ladder[k] = total(v)
        s = "---------- CURRENT LADDER ----------\n"
        users = sorted(ladder, key=lambda i: ladder[i], reverse=True)
        for userId in users:
            discord_user = discord.utils.find(
                lambda m: m.id == userId, ctx.message.channel.server.members)
            if discord_user is None:
                name = "USER NOT FOUND"
            else:
                name = discord_user.name
            if ladder[userId] == 1:
                s += '{} {} point\n'.format(name.ljust(30), ladder[userId])
            else:
                s += '{} {} points\n'.format(name.ljust(30), ladder[userId])
            if len(s) > 1000:
                await self.bot.say("```{}```".format(s))
                s = ""
        await self.bot.say("```{}```".format(s))


def setup(bot):
    bot.add_cog(predictCog(bot))
