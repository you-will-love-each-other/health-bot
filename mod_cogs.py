import asyncio
import random
import re
import discord
from discord.ext import commands
import useful
from useful import config, mod_team

class Modding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command()
    async def warn(self, ctx, *, arg):
        await useful.generic_modding_action(ctx, arg, "warn", "warned", 0xffa500)

    @commands.command()
    async def kick(self, ctx, *, arg):
        mod, members, _ = await useful.generic_modding_action(ctx, arg, "kick", "kicked", 0xffa500)
        if not(mod):
            return
        for member in members:
            await member.kick()

    @commands.command()
    async def ban(self, ctx, *, arg):
        mod, members, reason = await useful.generic_modding_action(ctx, arg, "ban", "banned", 0xff0000)
        if not(mod):
            return
        
        for member in members:
            await ctx.guild.ban(member, reason= reason, delete_message_seconds= 0)

    @commands.command()
    async def purgeban(self, ctx, *, arg):
        mod, members, reason = await useful.generic_modding_action(ctx, arg, "ban and message purge", "banned and their messages have been purged", 0xff0000)
        if not(mod):
            return
        
        for member in members:
            await ctx.guild.ban(member, reason= reason, delete_message_seconds= 604800)

    @commands.command()
    async def unban(self, ctx, *, arg):
        mod, _, reason = await useful.generic_modding_action(ctx, arg, "unban", "unbanned", 0x149414)
        if not(mod):
            return
        
        users = useful.get_unban_ids(arg)
        
        for user_id in users:
            user = await ctx.bot.fetch_user(user_id)
            if not(user):
                continue
            
            await ctx.guild.unban(user, reason= reason)

    @commands.command()
    async def mute(self, ctx, *, arg):
        mod, time, reason = useful.get_mute_info(ctx, arg)
        if not(mod):
            return
        
        if time[0]:
            _, members, _ = await useful.generic_modding_action(ctx, arg, "mute", f"muted for {time[0]}", 0xfffcbb, reason)
        else:
            _, members, _ = await useful.generic_modding_action(ctx, arg, "mute", "muted", 0xfffcbb, reason)

        muted_role = ctx.guild.get_role(config["MUTED_ROLE_ID"])
        for member in members:
            await member.add_roles(muted_role,reason="Muted", atomic=True)
            if time[1]:
                await asyncio.sleep(time[1])
                await member.remove_roles(muted_role, reason="Unmuted", atomic=True)

    @commands.command()
    async def unmute(self, ctx, *, arg):
        mod, members, _ = await useful.generic_modding_action(ctx, arg, "unmute", "unmuted", 0xfffcbb)
        if not(mod):
            return

        muted_role = ctx.guild.get_role(config["MUTED_ROLE_ID"])
        for member in members:
            await member.remove_roles(muted_role, reason="Unmuted", atomic=True)

    @commands.command()
    async def eject(self, ctx, *, arg):
        if not(useful.check_mod(ctx)):
                return
        members, reason = useful.get_modding_info(ctx, arg)
        for member in members:
            if ctx.author.top_role <= member.top_role:
                await ctx.send("You cannot eject this user.")
                continue
            user_message, mod_embed = useful.create_messages(member, reason, "ejected")
            modlog_embed, modlog = useful.create_modlog_embed(ctx, "eject", reason, 0xffa500, member)
            await modlog.send(embed= modlog_embed)

            try:
                await member.send(user_message)
            except:
                print(member.mention, "doesn't allow DMs.")

            await useful.eject_animation(ctx, member)
            await member.kick()
            await ctx.send(embed= mod_embed)

    @commands.command()
    async def baneject(self, ctx, *, arg):
        if not(useful.check_mod(ctx)):
                return
        members, reason = useful.get_modding_info(ctx, arg)
        for member in members:
            if ctx.author.top_role <= member.top_role:
                await ctx.send("You cannot ban eject this user.")
                continue
            user_message, mod_embed = useful.create_messages(member, reason, "ban ejected")
            modlog_embed, modlog = useful.create_modlog_embed(ctx, "ban eject", reason, 0xff0000, member)
            await modlog.send(embed= modlog_embed)

            try:
                await member.send(user_message)
            except:
                print(member.mention, "doesn't allow DMs.")

            await useful.eject_animation(ctx, member)
            await ctx.guild.ban(member, reason= reason, delete_message_days= 0)
            await ctx.send(embed= mod_embed)


class ModMisc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def spam(self, ctx, *, arg):
        if not(useful.check_mod(ctx)):
            return
        for x in range(int(arg)):
            await ctx.send("spam")

    @commands.command()
    async def purge(self, ctx, *, arg):
        if not(useful.check_mod(ctx)):
            return
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit= int(arg))
        deleted_text = ""
        users = []
        visited = []
        for message in deleted:
            if message.author not in visited:
                users.append((message.author,1))
                visited.append(message.author)
            else:
                i = visited.index(message.author)
                users[i] = (message.author,users[i][1] + 1)

        users.sort(reverse=True, key=lambda x:x[1])

        for (user, number_of_messages) in users:
            deleted_text += f"**{user.name}#{user.discriminator}:** {number_of_messages}\n"

        embed = discord.Embed(title=" ", description="Messages deleted:\n\n" + deleted_text, color=0xff0000)
        embed.set_author(name= f"{len(deleted)} messages purged | #{ctx.channel.name}")
        await ctx.bot.get_channel(config["MOD_LOG_ID"]).send(embed= embed)

    @commands.command()
    async def motd(self, ctx, *, arg):
        if not(useful.check_mod(ctx)):
            return
        
        motd_role = ctx.guild.get_role(config["MOTD_ROLE_ID"])
        members, _ = useful.get_modding_info(ctx, arg)

        for member in members:
            emojis = [697621015337107466,737315507509657661,697879872391086113,697880868743544903,753291933950017627,753291934008606762,804113756622684220,709794793051390153]
            emoji = ctx.bot.get_emoji(random.choice(emojis))
            await member.add_roles(motd_role,reason="Member of the day", atomic=True)
            motd_embed = discord.Embed(title=" ", description=f"{member.mention} is member of the day!", color=0xFFBF00)
            motd_embed.set_author(name= f"Member of the day")
            motd_message = await ctx.send(embed= motd_embed)
            await motd_message.add_reaction(emoji)
            await asyncio.sleep(86400)
            await member.remove_roles(motd_role,reason="Member of the day", atomic=True)