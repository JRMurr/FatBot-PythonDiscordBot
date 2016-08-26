import discord
from discord.ext import commands
from .utils import checks, config
import json


#target = open(filename, 'w')
#answer choices, dict with choices mapped to num votes
class poll:
    def __init__(self,pollName,answerCs,responses = {},active = True,allowMultiple=False):
        self.name = pollName.lower()
        #tmp = []
        #for choice in answerCs:
        #    tmp.append(choice.lower())
        self.answerChoices = answerCs
        self.responses = responses
        self.active = active
        self.allowMultiple = allowMultiple

class pollEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, poll):
            payload = obj.__dict__.copy()
            payload['__poll__'] = True
            return payload
        return json.JSONEncoder.default(self, obj)

def poll_decoder(obj):
    if '__poll__' in obj:
        return poll(obj['name'],obj['answerChoices'],obj['responses'],obj['active'],obj['allowMultiple'])
    return obj

class pollCog:
    """poll related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('polls.json',encoder=pollEncoder, object_hook=poll_decoder,
                                                 loop=bot.loop, load_later=True)
    @commands.command(pass_context=True,no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def create_poll(self,ctx,pollName, *args:str):
        "creates a poll, first argument is name, the rest are options"
        if pollName.lower() in self.config.all():
            if self.config.get(pollName.lower()).active:
                await self.bot.say("Poll with that name is active already")
            else:
                await self.bot.say("Poll with that name exsits but is not active, reply with 'y' or 'yes' to clear old responses")
                message = await self.bot.wait_for_message(author=ctx.message.author,timeout = 2.5)#2.5 sec timeout
                if message is None:
                    await self.bot.say("Did not respond fast enough")
                    return
                elif not (message.content.lower() == "y" or message.content.lower() == "yes"):
                    #dont overwrite
                    await self.bot.say("Not overwriting old poll")
                    return
        #poll doesnt already exist or user said to overwrite old one
        newPoll = poll(pollName.lower(),args)
        #await self.bot.say("name:{} choices:{} responses:{} active:{}".format(newPoll.name,newPoll.answerChoices,newPoll.responses,newPoll.active))
        #polls.update({newPoll.name:newPoll})
        await self.config.put(newPoll.name,newPoll)
        await self.bot.say("Created poll: " + newPoll.name)


    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def end_poll(self,pollName):
        """sets poll passed to not active if it exsits"""
        if pollName.lower() in self.config:
            #not sure if i have to re update the db
            poll = self.config.get((pollName.lower()))
            poll.active = False
            await self.config.put(poll.name,poll)
            await self.bot.say("Poll {} is now over".format(pollName.lower()))
        else:
            await self.bot.say("No poll with name:{} found".format(pollname.lower()))

   
    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remove_poll(self,pollName):        
        if not pollName.lower() in self.config.all():
            await self.bot.say("poll not found")
            return
        await self.config.remove(pollName.lower()) 
        await self.bot.say('poll removed')

    
    @commands.command(pass_context=True,no_pm=True)
    async def poll_vote(self,ctx,pollName,*args:str):
        """user gives poll name then anwer choice(s) they want to vote for"""
        if not pollName.lower() in self.config:
            await self.bot.say('poll not found, use !list_polls')
            return 
        poll = self.config.get(pollName.lower())
        if not poll.active:
            await self.bot.say('poll not active')
            return
        if len(args) < 1:
            await self.bot.say('not enough answer choices given')
            return
        if not poll.allowMultiple:
            if len(args)> 1:
                await self.bot.say('this poll only allows one answer choice per user')
                return
        userID = ctx.message.author.id
        responses = []
        for choice in args:
            for possibleAnswer in poll.answerChoices:
                if choice.lower() == possibleAnswer.lower():
                    responses.append(choice.lower())
                    break
            else:
                await self.bot.say(choice + ' not in possible answerChoices')
        poll.responses.update({userID:responses})
        await self.config.put(poll.name,poll)
        await self.bot.say('set responses for {} to {}'.format(poll.name,','.join(responses)))

    @commands.command()
    async def poll_results(self,pollName):
        if not pollName.lower() in self.config:
            await self.bot.say('poll not found, use !list_polls')
            return 
        poll = self.config.get(pollName.lower())
        numResponses = 0
        responses = {}
        for k in poll.responses:
        #k is user id, value for k is list of that users responses
            userResponses = poll.responses[k]
            numResponses+= len(userResponses) #make count 1 per user or total number of user responses?
            for tmp in userResponses:
                if tmp in responses:
                    count = responses[tmp]
                    count +=1
                    responses[tmp] = count
                else:
                    responses[tmp] = 1
        msg = 'Results:\n'
        for k in responses:
            msg+= '{}:{} votes\n'.format(k,responses[k])
        await self.bot.say(msg)

    @commands.command(no_pm=True)
    @checks.admin_or_permissions()
    async def list_polls(self):
        msg = 'Polls: '
        polls = self.config.all()
        for k in polls:
            msg+='('+ k + ': '
            if polls[k].active:
                msg+= 'active'
            else:
                msg+= 'not active'
            msg+=' Choices: ' + ','.join(polls[k].answerChoices)
            msg+= '), '
        await self.bot.say(msg)

    @commands.command(no_pm=True,hidden=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def debug_polls(self):
        msg = 'Polls: '
        for k in self.config.all():
            msg += str(self.config.get(k).__dict__) + '\n'
        await self.bot.say(msg)



def setup(bot):
    bot.add_cog(pollCog(bot))
