from dotenv import dotenv_values
import discord

config = dotenv_values('.env')


def checkmod(bot,ctx):
    healthguild = bot.get_guild(config['SERVER_ID'])
    mod = healthguild.get_role(config['MOD_ROLE_ID'])
    return mod in ctx.author.roles

def getvars(bot,ctx,arg,healthguild): # gets the user,reason and member for the mod functions
    userID = ""

    for x in range(len(arg)):
        if arg[x].isnumeric():
            userID += arg[x]
        if arg[x] == ">":
            break

    reason = arg[x+2:]
    userID = int(userID)
    user = bot.get_user(userID)
    member = healthguild.get_member(userID)

    return user,reason,member,userID

def modactions(ctx,user,reason,member,healthguild,mod,action): # writes the embed and dm for the mod functions
    if mod in ctx.author.roles and member.id != config['BOTS_OWN_ID']:
        if ctx.author.top_role > member.top_role or ctx.author.id == config['OWNER_ID']:
            if user.avatar:
                avatarurl = "https://cdn.discordapp.com/avatars/" + str(user.id) + "/" + user.avatar + ".webp"
            else:
                avatarurl = config['BOT_AVATAR']
            userstr = user.name + "#" + user.discriminator
            embed = False
            message = False
            if reason == "":
                embed=discord.Embed(title=" ", color=0xff0000)
                embed.set_author(name=userstr+" has been "+action+".", icon_url=avatarurl)
                message = "**You have been "+action+" by a moderator in HEALTHcord.**"
            else:
                embed=discord.Embed(title=" ", description="**Reason:** "+reason, color=0xff0000)
                embed.set_author(name=userstr+" has been "+action+".", icon_url=avatarurl)
                message = "**You have been "+action+" by a moderator in HEALTHcord.\nReason:** " + reason
            return embed,message
        return False, False
    else:
        return "notmod",False

def modlogembed(bot,action, reason, message, colour, user): # building the embed for the mod log channel
    modlog = bot.get_channel(config['MOD_LOG_ID'])
    serverid = str(message.guild.id)
    channelid = str(message.channel.id)
    messageid = str(message.message.id)
    messageurl = "https://discord.com/channels/" + serverid + "/" + channelid + "/" + messageid
    if not(reason):
        reason = "No reason given by the moderator."
    embed=discord.Embed(title= action + " | #" + message.channel.name, description= "**Offender:** " + user.mention + "\n**Reason:** " + reason + "\n**Responsible moderator: **" + message.author.mention,color=colour)
    embed.add_field(name="-----", value="[Jump to incident](" + messageurl + ")", inline=False)
    return embed, modlog

def timestrbuilder(seconds,secondsint,suffix):
    if seconds[-1] == "s":
        if secondsint == 1:
            suffix += " second"
        else:
            suffix += " seconds"
    elif seconds[-1] == "m":
        if secondsint == 1:
            suffix += " minute"
        else:
            suffix += " minutes"
        secondsint *= 60
    elif seconds[-1] == "h":
        if secondsint == 1:
            suffix += " hour"
        else:
            suffix += " hours"
        secondsint *= 60 * 60
    elif seconds[-1] == "d":
        if secondsint == 1:
            suffix += " day"
        else:
            suffix += " days"
        secondsint *= 60 * 60 * 24
    elif seconds[-1] == "y":
        if secondsint == 1:
            suffix += " year"
        else:
            suffix += " years"
        secondsint *= 60 * 60 * 24 * 365
    return suffix,secondsint
