from discord.ext import commands
import discord.utils

ADMIN_ROLES = ('BIG CHEESE','The Muscle','THE MEMER','admin')

def is_owner_check(message):
    return message.author.id == '83736990750605312'

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

def check_permissions(ctx, perms):
    msg = ctx.message
    if is_owner_check(msg):
        return True

    ch = msg.channel
    author = msg.author
    resolved = ch.permissions_for(author)
    for name,value in perms.items():
        msg = "checking: " + name
        if getattr(resolved, name, None) == value:
            msg = msg+ " has permisson"
        print(msg)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())

def role_or_permissions(ctx, check, **perms):
    print("checking: " + ctx.message.author.name)
    if check_permissions(ctx, perms):
        print("passed check permisson")
        return True

    ch = ctx.message.channel
    author = ctx.message.author
    if ch.is_private:
        return False # can't have roles in PMs

    role = discord.utils.find(check, author.roles)
    return role is not None

def role_or_admin(roleName,**perms):
    def predicate(ctx):
        return role_or_permissions(ctx,lambda r: r.name == roleName or r.name in ADMIN_ROLES,**perms)
    return commands.check(predicate)


def admin_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name in ADMIN_ROLES, **perms)

    return commands.check(predicate)
