import re
from bson.objectid import ObjectId
from discord.ext import commands

from .utils import checks

# Matches something like: "Bring back the quaaludes" - Quaaludes Guy
INPUT_REGEX = re.compile(r'"(?P<quote>.+)"\s*\-\s*(?P<source>(\S+\s*)+)')
OUTPUT_FORMAT = '"{quote}" - {source}'
OUTPUT_FORMAT_VERBOSE = '[{_id}] "{quote}" - {source}'
MAX_WHISPER_LENGTH = 1500


def setup(bot):
    bot.add_cog(QuotesCog(bot))


def format_quote(quote, show_id=False):
    fmt = OUTPUT_FORMAT_VERBOSE if show_id else OUTPUT_FORMAT
    return fmt.format(**quote)


class QuotesCog:
    """Commands for quotes"""

    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.db.quotes  # Get the relevant Mongo collection

    @commands.command()
    async def quote(self, *args):
        """
        Gets a random quote. If args are given, will get a quote that matches
        the args. The match is done against the quote text and the source.
        """

        # If words were provided, use them to filter the quotes
        if args:
            # Combine the given words with spaces and escape regex special chars
            query_str = ' '.join(args)
            # Caseless regex query for each field
            field_query = {
                '$regex': re.escape(query_str),
                '$options': 'i',  # Case-insensitive
            }
            # Mongo uses AND queries by default by we want OR
            query = {'$or': [
                {'quote': field_query},
                {'source': field_query},
            ]}
        else:
            query = {}  # Match all docs

        try:
            # Query for a random quote and print it
            quote = self.coll.aggregate([
                {'$match': query},  # Match against the query
                {'$sample': {'size': 1}},  # Select 1 random record
            ]).next()  # Will raise an error if there are no results
            await self.bot.say(format_quote(quote))
        except StopIteration:
            # No results from mongo
            await self.bot.say("No quotes!")

    # *args would not give ' " ' character for some reason
    @commands.command(pass_context=True)
    async def savequote(self, ctx):
        """
        Save the given quote
        """
        args = ctx.message.content.split(' ')
        msg = ' '.join(args[1:])
        match = INPUT_REGEX.match(msg)
        if match:
            self.coll.insert_one({
                'quote': match.group('quote'),
                'source': match.group('source'),
            })
            await self.bot.say("Added quote: " + msg)
        else:
            await self.bot.say("Quotes must be of the form '\"Quote\" - Source'")

    @commands.command()
    @checks.admin_or_permissions(manage_roles=True)
    async def showquotes(self):
        """Get all quotes, including their IDs"""
        quote_strs = [format_quote(quote, show_id=True) for quote in self.coll.find()]

        # Discord has a max length for whispers, so we may have to break up
        # the quote list into multiple messages to get around that. Build
        # a list of lists, where each sublist is a group of quotes that will
        # be merged into one message.
        quote_groups = [[]]  # [[<quote1>, <quote2>], [<quote3>, <quote4>]]
        last_group_size = 0
        for quote in quote_strs:
            last_group_size += (len(quote) + 1)  # +1 to account for newline char
            if last_group_size <= MAX_WHISPER_LENGTH:
                quote_group = quote_groups[-1]
            else:
                quote_group = []
                quote_groups.append(quote_group)
                last_group_size = 0
            quote_group.append(quote)

        # Merge each quote group into one string, then PM it
        for quote_group in quote_groups:
            msg = '\n'.join(quote_group)
            await self.bot.whisper(msg)

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def removequote(self, doc_id):
        """Remove a quote by its ID"""
        result = self.coll.delete_one({'_id': ObjectId(doc_id)})  # Adios, bitch
        response = f"Removed {doc_id}" \
            if result.deleted_count > 0 \
            else "Unknown doc ID"  # Nothing was deleted
        await self.bot.say(response)
