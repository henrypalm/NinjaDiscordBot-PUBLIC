import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

import discord
from discord.ext import commands

import config


def setup_logging():

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class BotLogging(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("discord_bot")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        self.logger.info(
            "Member joined: %s (%s)",
            member,
            member.id
        )

        channel = self.bot.get_channel(
            config.MOD_LOGS_CHANNEL_ID
        )

        if channel is None:
            return

        embed = discord.Embed(
            title="Member Joined",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="User",
            value=f"{member.mention}\n`{member.id}`"
        )

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        self.logger.info(
            "Member left: %s (%s)",
            member,
            member.id
        )

        channel = self.bot.get_channel(
            config.MOD_LOGS_CHANNEL_ID
        )

        if channel is None:
            return

        embed = discord.Embed(
            title="Member Left",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="User",
            value=f"{member}\n`{member.id}`"
        )

        await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    setup_logging()
    await bot.add_cog(BotLogging(bot))
