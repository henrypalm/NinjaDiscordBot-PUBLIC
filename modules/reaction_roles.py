import discord
from discord.ext import commands

import config


class ReactionRoles(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.role_messages = {
            # message_id: {
            #     emoji_id: role_id
            # }
        }

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload: discord.RawReactionActionEvent
    ):

        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in self.role_messages:
            return

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:
            return

        member = guild.get_member(payload.user_id)

        if member is None:
            return

        emoji_id = payload.emoji.id

        if emoji_id is None:
            return

        role_id = self.role_messages[
            payload.message_id
        ].get(emoji_id)

        if role_id is None:
            return

        role = guild.get_role(role_id)

        if role is None:
            return

        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self,
        payload: discord.RawReactionActionEvent
    ):

        if payload.message_id not in self.role_messages:
            return

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:
            return

        member = guild.get_member(payload.user_id)

        if member is None:
            return

        emoji_id = payload.emoji.id

        if emoji_id is None:
            return

        role_id = self.role_messages[
            payload.message_id
        ].get(emoji_id)

        if role_id is None:
            return

        role = guild.get_role(role_id)

        if role is None:
            return

        await member.remove_roles(role)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))
