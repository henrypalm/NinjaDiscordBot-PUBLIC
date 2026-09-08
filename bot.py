import discord
from discord.ext import commands
from discord import app_commands

import config


intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True


class NinjaBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=intents
        )

    async def setup_hook(self):
        await self.load_extension("modules.commands")
        await self.load_extension("modules.downloads")
        await self.load_extension("modules.welcome")
        await self.load_extension("modules.reaction_roles")
        await self.load_extension("modules.polls")
        await self.load_extension("modules.embeds")
        await self.load_extension("modules.moderation")
        await self.load_extension("modules.bot_logging")

        guild = discord.Object(id=config.GUILD_ID)

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

        print(f"Slash commands synced to guild {config.GUILD_ID}")

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print(f"Bot ID: {self.user.id}")

        for guild in self.guilds:
            print(f"Connected to: {guild.name} ({guild.id})")

        print("Bot is ready!")


bot = NinjaBot()

bot.run(config.BOT_TOKEN)
