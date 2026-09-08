import random

import discord
from discord.ext import commands

import config


class Welcome(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # =========================================================
    # Member Join
    # =========================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):

        #----------------
        # Assign Real Ninja Role
        #----------------

        role = member.guild.get_role(
            config.REAL_NINJA_ROLE_ID
        )

        if role is not None:

            try:

                await member.add_roles(
                    role,
                    reason="Automatically assigned upon joining the server."
                )

            except discord.Forbidden:

                print(
                    f"Unable to assign Real Ninja role to "
                    f"{member} ({member.id}). "
                    f"Check the bot's role hierarchy and permissions."
                )

            except discord.HTTPException as e:

                print(
                    f"Failed to assign Real Ninja role to "
                    f"{member} ({member.id}): {e}"
                )

        else:

            print(
                f"Real Ninja role "
                f"({config.REAL_NINJA_ROLE_ID}) "
                f"could not be found."
            )


        #----------------
        # Welcome Channel
        #----------------

        channel = self.bot.get_channel(
            config.WELCOME_CHANNEL_ID
        )

        if channel is None:
            return


        #----------------
        # Welcome Message
        #----------------

        message = random.choice(
            config.WELCOME_MESSAGES
        ).format(
            member=member.mention
        )

        embed = discord.Embed(
            title=config.WELCOME_TITLE,
            description=message,
            color=config.WELCOME_COLOR
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_image(
            url=config.WELCOME_IMAGE_URL
        )

        embed.set_footer(
            text=f"Welcome to the server, {member.name}!"
        )

        await channel.send(
            embed=embed
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Welcome(bot)
    )
