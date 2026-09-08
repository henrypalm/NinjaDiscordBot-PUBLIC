import discord
from discord import app_commands
from discord.ext import commands

import config


class DownloadView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label="Windows",
                style=discord.ButtonStyle.link,
                url=config.GAME_WINDOWS_URL,
                emoji="🪟"
            )
        )

        self.add_item(
            discord.ui.Button(
                label="Linux",
                style=discord.ButtonStyle.link,
                url=config.GAME_LINUX_URL,
                emoji="🐧"
            )
        )


class Downloads(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="download",
        description="Display the game download links."
    )
    @app_commands.default_permissions(administrator=True)
    async def download(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🥷 Download the Game",
            description=(
                "Choose your operating system below to "
                "download the latest version of the game."
            ),
            color=discord.Color.gold()
        )

        embed.add_field(
            name="🪟 Windows",
            value="Download the Windows version of the game.",
            inline=False
        )

        embed.add_field(
            name="🐧 Linux",
            value="Download the Linux version of the game.",
            inline=False
        )

        embed.set_footer(
            text="Goodwin Games • Thanks for playing!"
        )

        await interaction.response.send_message(
            embed=embed,
            view=DownloadView(),
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Downloads(bot))
