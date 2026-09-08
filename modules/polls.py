import discord
from discord import app_commands
from discord.ext import commands


class Polls(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="poll",
        description="Create a poll."
    )
    @app_commands.describe(
        question="The question for the poll.",
        option1="First option.",
        option2="Second option.",
        option3="Third option.",
        option4="Fourth option."
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None
    ):

        options = [
            option1,
            option2
        ]

        if option3:
            options.append(option3)

        if option4:
            options.append(option4)

        number_emojis = [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣"
        ]

        description = ""

        for index, option in enumerate(options):
            description += (
                f"{number_emojis[index]} {option}\n"
            )

        embed = discord.Embed(
            title="📊 Poll",
            description=description,
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text=f"Poll created by {interaction.user}"
        )

        await interaction.response.send_message(
            embed=embed
        )

        message = await interaction.original_response()

        for index in range(len(options)):
            await message.add_reaction(
                number_emojis[index]
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))
