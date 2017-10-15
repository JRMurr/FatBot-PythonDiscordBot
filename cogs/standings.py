import abc
import requests
from collections import defaultdict
from discord.ext import commands


def monospace(s):
    """
    Formats the given string as code for discord, so it becomes monospace
    """
    return '```\n{}```'.format(s)


LEAGUES = dict()  # This will be populated by the register_league annotation


def register_league(name):
    def inner(cls):
        LEAGUES[name] = cls()
        return cls
    return inner


class StandingsCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def standings(self, league):
        league = league.upper()
        try:
            # Get the function that processes this league
            league_obj = LEAGUES[league]
        except KeyError:
            await self.bot.say("Unsupported league {}. Supported leagues are {}".format(
                league, LEAGUES.keys()
            ))
            return
        result = league_obj.get_standings()
        if result:
            await self.bot.say(result)


class League(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_standings(self):
        pass


class NHLRecord:

    TEAM_ABBRS = {
        'Florida Panthers': 'FLA',
        'Montréal Canadiens': 'MTL',
        'Toronto Maple Leafs': 'TOR',
        'Tampa Bay Lightning': 'TBL',
        'Ottawa Senators': 'OTT',
        'Boston Bruins': 'BOS',
        'Buffalo Sabres': 'BUF',
        'Detroit Red Wings': 'DET',

        'Pittsburgh Penguins': 'PIT',
        'Philadelphia Flyers': 'PHI',
        'Washington Capitals': 'WSH',
        'New York Rangers': 'NYR',
        'Carolina Hurricanes': 'CAR',
        'New Jersey Devils': 'NJD',
        'New York Islanders': 'NYI',
        'Columbus Blue Jackets': 'CBJ',

        'St. Louis Blues': 'STL',
        'Colorado Avalanche': 'COL',
        'Dallas Stars': 'DAL',
        'Winnipeg Jets': 'WPG',
        'Minnesota Wild': 'MIN',
        'Nashville Predators': 'NSH',
        'Chicago Blackhawks': 'CHI',

        'Edmonton Oilers': 'EDM',
        'San Jose Sharks': 'SJS',
        'Arizona Coyotes': 'ARI',
        'Vancouver Canucks': 'VAN',
        'Calgary Flames': 'CGY',
        'Anaheim Ducks': 'ANA',
        'Los Angeles Kings': 'LAK',
        'Vegas Golden Knights': 'VGK',
    }
    FORMAT_STRING = "{abbr_name} | {gp:>2} | {wins:>2} | {losses:>2} |  {otl:>2} | {points:>3}"

    def __init__(self, conference, division, record_dict):
        self.conference = conference
        self.division = division
        self.long_name = record_dict['team']['name']
        self.abbr_name = NHLRecord.TEAM_ABBRS[self.long_name]
        self.gp = record_dict['gamesPlayed']
        self.wins = record_dict['leagueRecord']['wins']
        self.losses = record_dict['leagueRecord']['losses']
        self.otl = record_dict['leagueRecord']['ot']  # Overtime losses
        self.points = record_dict['points']  # Standings points
        self.ro_wins = record_dict['row']  # Regulation/overtime wins
        self.div_rank = int(record_dict['divisionRank'])  # These are strings for some reason
        self.wildcard_rank = int(record_dict['wildCardRank'])

    # Wildcard rank of 0 indicates this team is above the wildcard (top x in the division).
    # Anything greater than 0 is the team's rank among all teams in the conference that are
    # not in the top x of their division. The top x go into a list keyed by their division,
    # and the rest go into a list keyed by their conference. Each list contains tuples
    # of (record, rank) where rank is division rank for the top x lists, and wildcard rank
    # for all the rest.

    def get_section(self):
        if self.wildcard_rank:
            return self.conference
        return self.division

    def get_rank(self):
        if self.wildcard_rank:
            return self.wildcard_rank
        return self.div_rank

    def format(self):
        return self.FORMAT_STRING.format(**vars(self))


@register_league('NHL')
class NHL(League):

    DIVISION_PLAYOFF_SPOTS = 3  # Number of teams from each division that make the playoffs
    WILDCARD_PLAYOFF_SPOTS = 2  # Number of wildcard teams from each conference
    STANDINGS_URL = 'http://statsapi.web.nhl.com/api/v1/standings'
    OUTPUT_FMT = \
"""
```
EASTERN CONFERENCE
    | GP |  W |  L | OTL | PTS
----|----|----|----|-----|-----
{Metropolitan}
----|----|----|----|-----|-----
{Atlantic}
----|----|----|----|-----|-----
{Eastern}

WESTERN CONFERENCE
    | GP |  W |  L | OTL | PTS
----|----|----|----|-----|-----
{Central}
----|----|----|----|-----|-----
{Pacific}
----|----|----|----|-----|-----
{Western}
```
"""

    def get_standings(self):
        # Download the standings page
        response = requests.get(self.STANDINGS_URL)
        response.raise_for_status()
        data = response.json()  # Load the JSON response

        # Get each team in each division and add them all to one big list.
        records = []
        for div_dict in data['records']:
            conf = div_dict['conference']['name']
            div = div_dict['division']['name']
            records += (NHLRecord(conf, div, record) for record in div_dict['teamRecords'])

        sections = self._build_sections(records)
        section_strs = {sect: self._format_records(recs) for sect, recs in sections.items()}
        return NHL.OUTPUT_FMT.format(**section_strs)

    def _build_sections(self, records):
        sections = defaultdict(list)
        for record in records:
            sections[record.get_section()].append((record, record.get_rank()))

        # Sort all the value lists by their relevant rankings, and put them in a new dict
        for k, v in sections.items():
            # Each value is a list of (record, ranking) tuples, sort by ranking, then get rid of it
            sections[k] = [record for record, rank in sorted(v, key=lambda tup: tup[1])]
        return sections

    def _format_records(self, records):
        return '\n'.join(record.format() for record in records)


def setup(bot):
    bot.add_cog(StandingsCog(bot))
