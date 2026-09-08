import discord
from discord import app_commands
from discord.ext import commands

import config


class Commands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =========================
    # Ping
    # =========================

    @app_commands.command(
        name="ping",
        description="Check if the bot is responding."
    )
    async def ping(self, interaction: discord.Interaction):

        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"Pong! `{latency}ms`"
        )

    # =========================
    # Server Info
    # =========================

    @app_commands.command(
        name="serverinfo",
        description="Display information about the server."
    )
    async def serverinfo(self, interaction: discord.Interaction):

        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=guild.name,
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Members",
            value=str(guild.member_count)
        )

        embed.add_field(
            name="Channels",
            value=str(len(guild.channels))
        )

        embed.add_field(
            name="Server ID",
            value=str(guild.id)
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(
            embed=embed
        )

    # =========================
    # Say
    # =========================

    @app_commands.command(
        name="say",
        description="Send a message as the bot."
    )
    async def say(
        self,
        interaction: discord.Interaction,
        message: str
    ):

        if interaction.user.id != config.SERVER_OWNER_ID:
            await interaction.response.send_message(
                "You don't have permission to use this command.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Message sent.",
            ephemeral=True
        )

        await interaction.channel.send(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))
