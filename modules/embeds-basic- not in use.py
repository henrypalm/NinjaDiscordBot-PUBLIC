import discord
from discord import app_commands
from discord.ext import commands

import config


class EmbedBuilder(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =========================
    # Permission Check
    # =========================

    def has_embed_role(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if not isinstance(interaction.user, discord.Member):
            return False

        return any(
            role.id in config.EMBED_BUILDER_ROLE_IDS
            for role in interaction.user.roles
        )

    # =========================
    # Embed Command
    # =========================

    @app_commands.command(
        name="embed",
        description="Create and send an embedded message."
    )
    @app_commands.describe(
        title="The title of the embed.",
        description="The main body of the embed.",
        url="URL attached to the embed title.",
        color="Embed color in hexadecimal, such as FFD700.",
        content="Normal message content outside the embed."
    )
    async def embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        url: str = None,
        color: str = "FFD700",
        content: str = None
    ):

        # -------------------------
        # Permission Check
        # -------------------------

        if not self.has_embed_role(interaction):

            await interaction.response.send_message(
                "You don't have permission to use the embed builder.",
                ephemeral=True
            )

            return

        # -------------------------
        # Channel Check
        # -------------------------

        if (
            config.EMBED_BUILDER_CHANNEL_ID
            and interaction.channel_id
            != config.EMBED_BUILDER_CHANNEL_ID
        ):

            await interaction.response.send_message(
                "The embed builder can only be used in the designated channel.",
                ephemeral=True
            )

            return

        # -------------------------
        # Color
        # -------------------------

        try:

            color_value = int(
                color.replace("#", ""),
                16
            )

            embed_color = discord.Color(
                color_value
            )

        except ValueError:

            await interaction.response.send_message(
                "Invalid color. Use hexadecimal format, "
                "for example `FFD700`.",
                ephemeral=True
            )

            return

        # -------------------------
        # Create Embed
        # -------------------------

        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )

        # -------------------------
        # Title URL
        # -------------------------

        if url:
            embed.url = url

        # -------------------------
        # Send Message
        # -------------------------

        await interaction.response.send_message(
            content=content,
            embed=embed
        )


# =========================
# Setup
# =========================

async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedBuilder(bot))
