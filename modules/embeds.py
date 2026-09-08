import discord
from discord.ext import commands
from discord import app_commands

import config


# =============================================================
# Embed Data
# =============================================================

class EmbedData:
    def __init__(self):
        self.content = ""
        self.destination_channel_id = config.EMBED_BUILDER_CHANNEL_ID

        self.title = ""
        self.description = ""
        self.url = None
        self.color = 0xFFD700

        self.author_name = ""
        self.author_url = None
        self.author_icon_url = None

        self.thumbnail_url = None
        self.image_url = None

        self.footer_text = ""
        self.footer_icon_url = None

        self.fields = []

        # Editing information
        self.editing = False
        self.original_channel_id = None
        self.original_message_id = None


# =============================================================
# URL Validation
# =============================================================

def clean_url(value: str) -> str | None:

    value = value.strip()

    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        return None

    return value


# =============================================================
# Embed Builder
# =============================================================

class EmbedBuilder(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):

        self.bot = bot

        # Each user's active builder
        self.builders = {}


    # =========================================================
    # Permission
    # =========================================================

    def has_embed_role(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if not isinstance(
            interaction.user,
            discord.Member
        ):
            return False

        return any(
            role.id in config.EMBED_BUILDER_ROLE_IDS
            for role in interaction.user.roles
        )


    # =========================================================
    # Create Embed
    # =========================================================

    def build_embed(
        self,
        data: EmbedData
    ) -> discord.Embed:

        #----------------
        # Basic Embed
        #----------------

        embed = discord.Embed(
            title=data.title or None,
            description=data.description or None,
            url=data.url,
            color=data.color
        )


        #----------------
        # Author
        #----------------

        if data.author_name:

            if (
                data.author_url
                or data.author_icon_url
            ):

                embed.set_author(
                    name=data.author_name,
                    url=data.author_url,
                    icon_url=data.author_icon_url
                )

            else:

                embed.set_author(
                    name=data.author_name
                )


        #----------------
        # Images
        #----------------

        if data.thumbnail_url:

            embed.set_thumbnail(
                url=data.thumbnail_url
            )

        if data.image_url:

            embed.set_image(
                url=data.image_url
            )


        #----------------
        # Footer
        #----------------

        if data.footer_text:

            if data.footer_icon_url:

                embed.set_footer(
                    text=data.footer_text,
                    icon_url=data.footer_icon_url
                )

            else:

                embed.set_footer(
                    text=data.footer_text
                )


        #----------------
        # Fields
        #----------------

        for field in data.fields:

            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"]
            )


        #----------------
        # Empty Embed Protection
        #----------------

        # Discord does not allow a completely empty embed.

        if (
            not embed.title
            and not embed.description
            and not embed.fields
            and not embed.author
            and not embed.footer
            and not embed.image.url
            and not embed.thumbnail.url
        ):

            embed.description = "\u200b"


        return embed


    # =========================================================
    # Create New Embed
    # =========================================================

    @app_commands.command(
        name="embed",
        description="Open the embed builder."
    )
    async def embed(
        self,
        interaction: discord.Interaction
    ):

        #----------------
        # Permission
        #----------------

        if not self.has_embed_role(interaction):

            await interaction.response.send_message(
                "You don't have permission to use the embed builder.",
                ephemeral=True
            )

            return


        #----------------
        # Channel Check
        #----------------

        if (
            config.EMBED_BUILDER_CHANNEL_ID
            and interaction.channel_id
            != config.EMBED_BUILDER_CHANNEL_ID
        ):

            await interaction.response.send_message(
                "The embed builder can only be used "
                "in the designated channel.",
                ephemeral=True
            )

            return


        #----------------
        # Create Builder
        #----------------

        data = EmbedData()

        self.builders[
            interaction.user.id
        ] = data

        embed = self.build_embed(
            data
        )

        view = EmbedBuilderView(
            self,
            interaction.user.id
        )


        #----------------
        # Send Builder
        #----------------

        await interaction.response.send_message(
            content=(
                "### 🛠️ Embed Builder\n"
                "Configure your embed using the buttons below."
            ),
            embed=embed,
            view=view,
            ephemeral=True
        )


    # =========================================================
    # Edit Existing Embed
    # =========================================================

    @app_commands.command(
        name="editembed",
        description="Edit an existing bot message using its Discord message link."
    )
    async def editembed(
        self,
        interaction: discord.Interaction,
        message_link: str
    ):

        #----------------
        # Permission
        #----------------

        if not self.has_embed_role(interaction):

            await interaction.response.send_message(
                "❌ You do not have permission to use the embed builder.",
                ephemeral=True
            )

            return


        #----------------
        # Channel Check
        #----------------

        if (
            config.EMBED_BUILDER_CHANNEL_ID
            and interaction.channel_id
            != config.EMBED_BUILDER_CHANNEL_ID
        ):

            await interaction.response.send_message(
                f"❌ Use this command in "
                f"<#{config.EMBED_BUILDER_CHANNEL_ID}>.",
                ephemeral=True
            )

            return


        #----------------
        # Parse Message Link
        #----------------

        try:

            parts = message_link.strip().split("/")

            if len(parts) < 3:
                raise ValueError

            message_id = int(parts[-1])
            channel_id = int(parts[-2])
            guild_id = int(parts[-3])

        except (ValueError, IndexError):

            await interaction.response.send_message(
                "❌ Invalid Discord message link.",
                ephemeral=True
            )

            return


        #----------------
        # Server Check
        #----------------

        if guild_id != interaction.guild_id:

            await interaction.response.send_message(
                "❌ That message is not from this server.",
                ephemeral=True
            )

            return


        #----------------
        # Get Channel
        #----------------

        channel = self.bot.get_channel(
            channel_id
        )

        if channel is None:

            await interaction.response.send_message(
                "❌ I could not access that channel.",
                ephemeral=True
            )

            return


        #----------------
        # Get Message
        #----------------

        try:

            message = await channel.fetch_message(
                message_id
            )

        except discord.NotFound:

            await interaction.response.send_message(
                "❌ That message could not be found.",
                ephemeral=True
            )

            return

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ I do not have permission to access that message.",
                ephemeral=True
            )

            return


        #----------------
        # Bot Message Check
        #----------------

        if message.author.id != self.bot.user.id:

            await interaction.response.send_message(
                "❌ I can only edit messages sent by this bot.",
                ephemeral=True
            )

            return


        #----------------
        # Multiple Embed Check
        #----------------

        if len(message.embeds) > 1:

            await interaction.response.send_message(
                "❌ This message contains multiple embeds, "
                "which the builder does not currently support.",
                ephemeral=True
            )

            return


        #----------------
        # Create Edit Data
        #----------------

        data = EmbedData()

        data.editing = True

        data.original_channel_id = channel_id
        data.original_message_id = message_id

        # Start with the original channel as the destination
        data.destination_channel_id = channel_id


        #----------------
        # Load Message Content
        #----------------

        data.content = message.content or ""


        #----------------
        # Load Embed
        #----------------

        if message.embeds:

            embed = message.embeds[0]

            data.title = embed.title or ""

            data.description = (
                embed.description or ""
            )

            data.url = clean_url(
                embed.url or ""
            )

            if embed.color:

                data.color = embed.color.value


            #----------------
            # Author
            #----------------

            if embed.author:

                data.author_name = (
                    embed.author.name or ""
                )

                data.author_url = clean_url(
                    embed.author.url or ""
                )

                data.author_icon_url = clean_url(
                    embed.author.icon_url or ""
                )


            #----------------
            # Images
            #----------------

            if embed.thumbnail:

                data.thumbnail_url = clean_url(
                    embed.thumbnail.url or ""
                )

            if embed.image:

                data.image_url = clean_url(
                    embed.image.url or ""
                )


            #----------------
            # Footer
            #----------------

            if embed.footer:

                data.footer_text = (
                    embed.footer.text or ""
                )

                data.footer_icon_url = clean_url(
                    embed.footer.icon_url or ""
                )


            #----------------
            # Fields
            #----------------

            for field in embed.fields:

                data.fields.append({
                    "name": field.name,
                    "value": field.value,
                    "inline": field.inline
                })


        #----------------
        # Save Builder
        #----------------

        self.builders[
            interaction.user.id
        ] = data


        #----------------
        # Build Preview
        #----------------

        embed = self.build_embed(
            data
        )

        view = EmbedBuilderView(
            self,
            interaction.user.id
        )


        #----------------
        # Send Editor
        #----------------

        await interaction.response.send_message(
            content=(
                "✏️ **Editing Existing Message**\n"
                f"Current message: {message.jump_url}\n\n"
                "Make your changes below, then select "
                "**Update**."
            ),
            embed=embed,
            view=view,
            ephemeral=True
        )
        
# =============================================================
# Field Modal
# =============================================================

class FieldModal(discord.ui.Modal):

    def __init__(
        self,
        cog,
        user_id,
        field_index=None,
        inline=False
    ):

        super().__init__(
            title=(
                "Add Field"
                if field_index is None
                else "Edit Field"
            )
        )

        self.cog = cog
        self.user_id = user_id
        self.field_index = field_index
        self.inline = inline

        data = cog.builders[user_id]

        #----------------
        # Existing Values
        #----------------

        if field_index is not None:

            field = data.fields[field_index]

            name = field["name"]
            value = field["value"]

        else:

            name = ""
            value = ""

        #----------------
        # Field Name
        #----------------

        self.name_input = discord.ui.TextInput(
            label="Field Name",
            placeholder="Enter the field name...",
            default=name,
            max_length=256,
            required=True
        )

        self.add_item(
            self.name_input
        )

        #----------------
        # Field Value
        #----------------

        self.value_input = discord.ui.TextInput(
            label="Field Value",
            placeholder="Enter the field value...",
            default=value,
            style=discord.TextStyle.paragraph,
            max_length=1024,
            required=True
        )

        self.add_item(
            self.value_input
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        #----------------
        # Permission
        #----------------

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders.get(
            self.user_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Your embed builder has expired.",
                ephemeral=True
            )

            return

        #----------------
        # Create Field
        #----------------

        field = {
            "name": self.name_input.value.strip(),
            "value": self.value_input.value.strip(),
            "inline": self.inline
        }

        #----------------
        # Edit Existing
        #----------------

        if self.field_index is not None:

            data.fields[
                self.field_index
            ] = field

            message = "✅ Field updated."

        else:

            # Discord allows a maximum
            # of 25 fields per embed.

            if len(data.fields) >= 25:

                await interaction.response.send_message(
                    "❌ Discord embeds can only have "
                    "25 fields.",
                    ephemeral=True
                )

                return

            data.fields.append(
                field
            )

            message = "✅ Field added."

        #----------------
        # Return to Builder
        #----------------

        embed = self.cog.build_embed(
            data
        )

        view = EmbedBuilderView(
            self.cog,
            self.user_id
        )

        await interaction.response.edit_message(
            content=(
                "### 🛠️ Embed Builder\n"
                f"{message}"
            ),
            embed=embed,
            view=view
        )
        
        
# =============================================================
# Field Inline Selection View
# =============================================================

class FieldInlineView(discord.ui.View):

    def __init__(
        self,
        cog,
        user_id,
        field_index=None
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog
        self.user_id = user_id
        self.field_index = field_index

    # =========================================================
    # Full Width
    # =========================================================

    @discord.ui.button(
        label="Full Width",
        emoji="❌",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def full_width(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            FieldModal(
                self.cog,
                self.user_id,
                self.field_index,
                inline=False
            )
        )

    # =========================================================
    # Inline
    # =========================================================

    @discord.ui.button(
        label="Inline",
        emoji="✅",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def inline(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            FieldModal(
                self.cog,
                self.user_id,
                self.field_index,
                inline=True
            )
        )

    # =========================================================
    # Cancel
    # =========================================================

    @discord.ui.button(
        label="Cancel",
        emoji="↩️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders.get(
            self.user_id
        )

        if data is None:

            await interaction.response.edit_message(
                content="❌ Your embed builder has expired.",
                embed=None,
                view=None
            )

            return

        await interaction.response.edit_message(
            content="### 🧱 Embed Fields",
            embed=self.cog.build_embed(data),
            view=FieldManagerView(
                self.cog,
                self.user_id
            )
        )
        
        
        
# =============================================================
# Field Manager View
# =============================================================

class FieldManagerView(discord.ui.View):

    def __init__(
        self,
        cog,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog
        self.user_id = user_id

        data = cog.builders[user_id]


    # =========================================================
    # Add Field
    # =========================================================

    @discord.ui.button(
        label="Add Field",
        emoji="➕",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def add_field(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders[self.user_id]

        if len(data.fields) >= 25:

            await interaction.response.send_message(
                "❌ Discord embeds can only have 25 fields.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content=(
                "### 🧱 Add Field\n\n"
                "Choose how this field should be displayed."
            ),
            embed=None,
            view=FieldInlineView(
                self.cog,
                self.user_id
            )
        )


    # =========================================================
    # Edit Field
    # =========================================================

    @discord.ui.button(
        label="Edit Field",
        emoji="✏️",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def edit_field(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders[self.user_id]

        if not data.fields:

            await interaction.response.send_message(
                "❌ There are no fields to edit.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content="### ✏️ Select a field to edit.",
            embed=None,
            view=FieldEditView(
                self.cog,
                self.user_id
            )
        )


    # =========================================================
    # Remove Field
    # =========================================================

    @discord.ui.button(
        label="Remove Field",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def remove_field(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders[self.user_id]

        if not data.fields:

            await interaction.response.send_message(
                "❌ There are no fields to remove.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content="### 🗑️ Select a field to remove.",
            embed=None,
            view=FieldRemoveView(
                self.cog,
                self.user_id
            )
        )


    # =========================================================
    # Back
    # =========================================================

    @discord.ui.button(
        label="Back",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders[self.user_id]

        embed = self.cog.build_embed(
            data
        )

        view = EmbedBuilderView(
            self.cog,
            self.user_id
        )

        await interaction.response.edit_message(
            content="### 🛠️ Embed Builder",
            embed=embed,
            view=view
        )

# =============================================================
# Field Edit View
# =============================================================

class FieldEditView(discord.ui.View):

    def __init__(
        self,
        cog,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog
        self.user_id = user_id

        data = cog.builders[user_id]

        options = []

        for index, field in enumerate(
            data.fields
        ):

            label = field["name"]

            if len(label) > 100:
                label = label[:97] + "..."

            options.append(
                discord.SelectOption(
                    label=label,
                    value=str(index),
                    description=(
                        "Inline"
                        if field["inline"]
                        else "Full width"
                    )
                )
            )

        self.add_item(
            FieldEditSelect(
                cog,
                user_id,
                options
            )
        )


    # =========================================================
    # Back
    # =========================================================

    @discord.ui.button(
        label="Back",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders[self.user_id]

        await interaction.response.edit_message(
            content="### 🧱 Embed Fields",
            embed=self.cog.build_embed(data),
            view=FieldManagerView(
                self.cog,
                self.user_id
            )
        )


# =============================================================
# Field Edit Select
# =============================================================

class FieldEditSelect(discord.ui.Select):

    def __init__(
        self,
        cog,
        user_id,
        options
    ):

        self.cog = cog
        self.user_id = user_id

        super().__init__(
            placeholder="Select a field...",
            options=options,
            min_values=1,
            max_values=1
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        field_index = int(
            self.values[0]
        )

        data = self.cog.builders.get(
            self.user_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Your embed builder has expired.",
                ephemeral=True
            )

            return

        if field_index >= len(data.fields):

            await interaction.response.send_message(
                "❌ That field no longer exists.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content=(
                "### ✏️ Edit Field\n\n"
                "Choose how this field should be displayed."
            ),
            embed=None,
            view=FieldInlineView(
                self.cog,
                self.user_id,
                field_index
            )
        )

# =============================================================
# Field Remove View
# =============================================================

class FieldRemoveView(discord.ui.View):

    def __init__(
        self,
        cog,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog
        self.user_id = user_id

        data = cog.builders[user_id]

        options = []

        for index, field in enumerate(
            data.fields
        ):

            label = field["name"]

            if len(label) > 100:
                label = label[:97] + "..."

            options.append(
                discord.SelectOption(
                    label=label,
                    value=str(index)
                )
            )

        self.add_item(
            FieldRemoveSelect(
                cog,
                user_id,
                options
            )
        )


    # =========================================================
    # Back
    # =========================================================

    @discord.ui.button(
        label="Back",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders[self.user_id]

        await interaction.response.edit_message(
            content="### 🧱 Embed Fields",
            embed=self.cog.build_embed(data),
            view=FieldManagerView(
                self.cog,
                self.user_id
            )
        )


# =============================================================
# Field Remove Select
# =============================================================

class FieldRemoveSelect(discord.ui.Select):

    def __init__(
        self,
        cog,
        user_id,
        options
    ):

        self.cog = cog
        self.user_id = user_id

        super().__init__(
            placeholder="Select a field to remove...",
            options=options,
            min_values=1,
            max_values=1
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        field_index = int(
            self.values[0]
        )

        data = self.cog.builders.get(
            self.user_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Your embed builder has expired.",
                ephemeral=True
            )

            return

        if field_index >= len(data.fields):

            await interaction.response.send_message(
                "❌ That field no longer exists.",
                ephemeral=True
            )

            return

        removed_field = data.fields.pop(
            field_index
        )

        embed = self.cog.build_embed(
            data
        )

        await interaction.response.edit_message(
            content=(
                "### 🧱 Embed Fields\n"
                f"✅ Removed **{removed_field['name']}**."
            ),
            embed=embed,
            view=FieldManagerView(
                self.cog,
                self.user_id
            )
        )

# =============================================================
# Embed Builder View
# =============================================================

class EmbedBuilderView(
    discord.ui.View
):

    def __init__(
        self,
        cog: EmbedBuilder,
        user_id: int
    ):

        super().__init__(
            timeout=900
        )

        self.cog = cog
        self.user_id = user_id
        
        data = cog.builders.get(
            user_id
        )

        if data and data.editing:
            self.send.label = "Update"


    # =========================================================
    # User Check
    # =========================================================

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return False

        return True


    # =========================================================
    # Basic
    # =========================================================

    @discord.ui.button(
        label="Basic",
        emoji="📝",
        style=discord.ButtonStyle.primary
    )
    async def basic(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.builders[
            self.user_id
        ]

        modal = BasicModal(
            data
        )

        await interaction.response.send_modal(
            modal
        )


    # =========================================================
    # Author
    # =========================================================

    @discord.ui.button(
        label="Author",
        emoji="👤",
        style=discord.ButtonStyle.secondary
    )
    async def author(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.builders[
            self.user_id
        ]

        modal = AuthorModal(
            data
        )

        await interaction.response.send_modal(
            modal
        )


    # =========================================================
    # Images
    # =========================================================

    @discord.ui.button(
        label="Images",
        emoji="🖼️",
        style=discord.ButtonStyle.secondary
    )
    async def images(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.builders[
            self.user_id
        ]

        modal = ImagesModal(
            data
        )

        await interaction.response.send_modal(
            modal
        )


    # =========================================================
    # Footer
    # =========================================================

    @discord.ui.button(
        label="Footer",
        emoji="📌",
        style=discord.ButtonStyle.secondary
    )
    async def footer(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.builders[
            self.user_id
        ]

        modal = FooterModal(
            data
        )

        await interaction.response.send_modal(
            modal
        )


    
    # =========================================================
    # Fields
    # =========================================================

    @discord.ui.button(
        label="Fields",
        emoji="🧱",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def fields(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return

        data = self.cog.builders.get(
            self.user_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Your embed builder has expired.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content=(
                "### 🧱 Embed Fields\n"
                "Add, edit, or remove fields from your embed."
            ),
            embed=self.cog.build_embed(data),
            view=FieldManagerView(
                self.cog,
                self.user_id
            )
        )


    # =========================================================
    # Destination
    # =========================================================

    @discord.ui.button(
        label="Destination",
        emoji="📍",
        style=discord.ButtonStyle.secondary
    )
    async def destination(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.builders[
            self.user_id
        ]

        view = DestinationView(
            self.cog,
            self.user_id
        )

        current_channel = None

        if data.destination_channel_id:

            current_channel = interaction.guild.get_channel(
                data.destination_channel_id
            )

        if current_channel:

            content = (
                f"📍 **Current destination:** "
                f"{current_channel.mention}\n\n"
                "Select a different channel below."
            )

        else:

            content = (
                "📍 **Current destination:** "
                "Not selected\n\n"
                "Select the channel where this "
                "embed should be posted."
            )

        await interaction.response.send_message(
            content=content,
            view=view,
            ephemeral=True
        )


    # =========================================================
    # Preview
    # =========================================================

    @discord.ui.button(
        label="Preview",
        emoji="👁️",
        style=discord.ButtonStyle.success
    )
    async def preview(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.builders[
            self.user_id
        ]

        embed = self.cog.build_embed(
            data
        )

        await interaction.response.send_message(
            content=data.content or None,
            embed=embed,
            ephemeral=True
        )


    # =========================================================
    # Send / Update
    # =========================================================

    @discord.ui.button(
        label="Send",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def send(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.builders.get(
            self.user_id
        )

        if not data:

            await interaction.response.send_message(
                "❌ This embed builder has expired.",
                ephemeral=True
            )

            return


        #----------------
        # Destination Check
        #----------------

        if not data.destination_channel_id:

            await interaction.response.send_message(
                "❌ Please select a destination channel first.",
                ephemeral=True
            )

            return


        #----------------
        # Get Destination
        #----------------

        destination = self.cog.bot.get_channel(
            data.destination_channel_id
        )

        if destination is None:

            await interaction.response.send_message(
                "❌ I could not access the destination channel.",
                ephemeral=True
            )

            return


        #----------------
        # Build Embed
        #----------------

        embed = self.cog.build_embed(
            data
        )


        try:

            #==================================================
            # EDIT EXISTING MESSAGE
            #==================================================

            if data.editing:

                original_channel = (
                    self.cog.bot.get_channel(
                        data.original_channel_id
                    )
                )

                if original_channel is None:

                    await interaction.response.send_message(
                        "❌ I could not access the original message channel.",
                        ephemeral=True
                    )

                    return


                #----------------
                # Get Original Message
                #----------------

                try:

                    original_message = (
                        await original_channel.fetch_message(
                            data.original_message_id
                        )
                    )

                except discord.NotFound:

                    await interaction.response.send_message(
                        "❌ The original message no longer exists.",
                        ephemeral=True
                    )

                    return


                #==================================================
                # SAME CHANNEL
                #==================================================

                if (
                    data.destination_channel_id
                    == data.original_channel_id
                ):

                    await original_message.edit(
                        content=data.content or None,
                        embeds=[embed]
                    )

                    self.cog.builders.pop(
                        self.user_id,
                        None
                    )

                    await interaction.response.edit_message(
                        content=(
                            "✅ **Message updated successfully.**"
                        ),
                        embed=None,
                        view=None
                    )

                    return


                #==================================================
                # DIFFERENT CHANNEL
                #==================================================

                new_message = await destination.send(
                    content=data.content or None,
                    embed=embed
                )

                # Only delete the original after the new
                # message was successfully created.

                await original_message.delete()

                self.cog.builders.pop(
                    self.user_id,
                    None
                )

                await interaction.response.edit_message(
                    content=(
                        "✅ **Message moved and updated successfully.**\n"
                        f"New location: {new_message.jump_url}"
                    ),
                    embed=None,
                    view=None
                )

                return


            #==================================================
            # CREATE NEW MESSAGE
            #==================================================

            message = await destination.send(
                content=data.content or None,
                embed=embed
            )

            self.cog.builders.pop(
                self.user_id,
                None
            )

            await interaction.response.edit_message(
                content=(
                    "✅ **Embed sent successfully.**\n"
                    f"{message.jump_url}"
                ),
                embed=None,
                view=None
            )


        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ I do not have permission to send or edit "
                "messages in that channel.",
                ephemeral=True
            )

        except discord.HTTPException as e:

            await interaction.response.send_message(
                f"❌ Discord rejected the message:\n`{e}`",
                ephemeral=True
            )

    # =========================================================
    # Cancel
    # =========================================================

    @discord.ui.button(
        label="Cancel",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.cog.builders.pop(
            self.user_id,
            None
        )

        await interaction.response.edit_message(
            content="❌ Embed builder cancelled.",
            embed=None,
            view=None
        )


# =============================================================
# Destination View
# =============================================================

class DestinationView(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=300)
        self.cog = cog
        self.user_id = user_id

        data = cog.builders[user_id]

        options = []

        for channel_id in config.EMBED_DESTINATION_CHANNEL_IDS:
            channel = cog.bot.get_channel(channel_id)

            if channel:
                options.append(
                    discord.SelectOption(
                        label=channel.name,
                        value=str(channel.id),
                        default=(data.destination_channel_id == channel.id)
                    )
                )

        if options:
            self.add_item(DestinationSelect(cog, user_id, options))


# =============================================================
# Destination Select
# =============================================================

class DestinationSelect(discord.ui.Select):

    def __init__(
        self,
        cog,
        user_id,
        options
    ):

        self.cog = cog
        self.user_id = user_id

        super().__init__(
            placeholder="Select a destination channel...",
            options=options,
            min_values=1,
            max_values=1
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        #----------------
        # User Check
        #----------------

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "This is someone else's embed builder.",
                ephemeral=True
            )

            return


        #----------------
        # Get Selected Channel
        #----------------

        channel_id = int(
            self.values[0]
        )

        channel = self.cog.bot.get_channel(
            channel_id
        )

        if channel is None:

            await interaction.response.send_message(
                "❌ I could not find that channel.",
                ephemeral=True
            )

            return


        #----------------
        # Save Destination
        #----------------

        data = self.cog.builders[
            self.user_id
        ]

        data.destination_channel_id = channel_id


        #----------------
        # Confirm Selection
        #----------------

        await interaction.response.edit_message(
            content=(
                f"✅ Destination set to "
                f"{channel.mention}."
            ),
            view=None
        )


# =============================================================
# Basic Modal
# =============================================================

class BasicModal(
    discord.ui.Modal
):

    def __init__(
        self,
        data: EmbedData
    ):

        super().__init__(
            title="Basic Embed Settings"
        )

        self.data = data


        #----------------
        # Title
        #----------------

        self.title_input = discord.ui.TextInput(
            label="Title",
            placeholder="Enter the embed title...",
            required=False,
            max_length=256,
            default=data.title
        )


        #----------------
        # Description
        #----------------

        self.description_input = discord.ui.TextInput(
            label="Description",
            placeholder="Enter the embed body...",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=4000,
            default=data.description
        )


        #----------------
        # Title URL
        #----------------

        self.url_input = discord.ui.TextInput(
            label="Title URL",
            placeholder="https://example.com",
            required=False,
            default=data.url or ""
        )


        #----------------
        # Color
        #----------------

        self.color_input = discord.ui.TextInput(
            label="Color",
            placeholder="FFD700",
            required=False,
            max_length=6,
            default=f"{data.color:06X}"
        )


        #----------------
        # Message Content
        #----------------

        self.content_input = discord.ui.TextInput(
            label="Message Content",
            placeholder="Text outside the embed...",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=2000,
            default=data.content
        )


        self.add_item(
            self.title_input
        )

        self.add_item(
            self.description_input
        )

        self.add_item(
            self.url_input
        )

        self.add_item(
            self.color_input
        )

        self.add_item(
            self.content_input
        )


    async def on_submit(
        self,
        interaction: discord.Interaction
    ):


        #----------------
        # Save Basic Data
        #----------------

        self.data.title = (
            self.title_input.value.strip()
        )

        self.data.description = (
            self.description_input.value.strip()
        )

        self.data.content = (
            self.content_input.value.strip()
        )


        #----------------
        # Title URL
        #----------------

        url = clean_url(
            self.url_input.value
        )

        if (
            self.url_input.value.strip()
            and not url
        ):

            await interaction.response.send_message(
                "❌ Invalid Title URL. "
                "Use a URL beginning with "
                "`http://` or `https://`.",
                ephemeral=True
            )

            return

        self.data.url = url


        #----------------
        # Color
        #----------------

        if self.color_input.value:

            color_value = (
                self.color_input.value
                .replace("#", "")
                .strip()
            )

            try:

                color = int(
                    color_value,
                    16
                )

            except ValueError:

                await interaction.response.send_message(
                    "❌ Invalid color. "
                    "Use a hexadecimal color like `FFD700`.",
                    ephemeral=True
                )

                return


            # Discord embed colors use a 24-bit RGB value.
            if not 0x000000 <= color <= 0xFFFFFF:

                await interaction.response.send_message(
                    "❌ Invalid color. "
                    "Use a hexadecimal color between "
                    "`000000` and `FFFFFF`.",
                    ephemeral=True
                )

                return


            self.data.color = color


        await interaction.response.send_message(
            "✅ Basic settings updated.",
            ephemeral=True
        )


# =============================================================
# Author Modal
# =============================================================

class AuthorModal(
    discord.ui.Modal
):

    def __init__(
        self,
        data: EmbedData
    ):

        super().__init__(
            title="Author Settings"
        )

        self.data = data


        #----------------
        # Author Name
        #----------------

        self.name_input = discord.ui.TextInput(
            label="Author Name",
            required=False,
            max_length=256,
            default=data.author_name
        )


        #----------------
        # Author URL
        #----------------

        self.url_input = discord.ui.TextInput(
            label="Author URL",
            placeholder="https://example.com",
            required=False,
            default=data.author_url or ""
        )


        #----------------
        # Author Avatar URL
        #----------------

        self.icon_input = discord.ui.TextInput(
            label="Author Avatar URL",
            placeholder="https://example.com/avatar.png",
            required=False,
            default=data.author_icon_url or ""
        )


        self.add_item(
            self.name_input
        )

        self.add_item(
            self.url_input
        )

        self.add_item(
            self.icon_input
        )


    async def on_submit(
        self,
        interaction: discord.Interaction
    ):


        #----------------
        # Author Name
        #----------------

        self.data.author_name = (
            self.name_input.value.strip()
        )


        #----------------
        # Author URL
        #----------------

        url = clean_url(
            self.url_input.value
        )

        if (
            self.url_input.value.strip()
            and not url
        ):

            await interaction.response.send_message(
                "❌ Invalid Author URL. "
                "Use a URL beginning with "
                "`http://` or `https://`.",
                ephemeral=True
            )

            return

        self.data.author_url = url


        #----------------
        # Author Avatar URL
        #----------------

        icon_url = clean_url(
            self.icon_input.value
        )

        if (
            self.icon_input.value.strip()
            and not icon_url
        ):

            await interaction.response.send_message(
                "❌ Invalid Author Avatar URL. "
                "Use a URL beginning with "
                "`http://` or `https://`.",
                ephemeral=True
            )

            return

        self.data.author_icon_url = icon_url


        await interaction.response.send_message(
            "✅ Author settings updated.",
            ephemeral=True
        )


# =============================================================
# Images Modal
# =============================================================

class ImagesModal(
    discord.ui.Modal
):

    def __init__(
        self,
        data: EmbedData
    ):

        super().__init__(
            title="Image Settings"
        )

        self.data = data


        #----------------
        # Thumbnail URL
        #----------------

        self.thumbnail_input = discord.ui.TextInput(
            label="Thumbnail URL",
            placeholder="https://example.com/image.png",
            required=False,
            default=data.thumbnail_url or ""
        )


        #----------------
        # Main Image URL
        #----------------

        self.image_input = discord.ui.TextInput(
            label="Main Image URL",
            placeholder="https://example.com/image.png",
            required=False,
            default=data.image_url or ""
        )


        self.add_item(
            self.thumbnail_input
        )

        self.add_item(
            self.image_input
        )


    async def on_submit(
        self,
        interaction: discord.Interaction
    ):


        #----------------
        # Thumbnail URL
        #----------------

        thumbnail_url = clean_url(
            self.thumbnail_input.value
        )

        if (
            self.thumbnail_input.value.strip()
            and not thumbnail_url
        ):

            await interaction.response.send_message(
                "❌ Invalid Thumbnail URL. "
                "Use a URL beginning with "
                "`http://` or `https://`.",
                ephemeral=True
            )

            return

        self.data.thumbnail_url = thumbnail_url


        #----------------
        # Main Image URL
        #----------------

        image_url = clean_url(
            self.image_input.value
        )

        if (
            self.image_input.value.strip()
            and not image_url
        ):

            await interaction.response.send_message(
                "❌ Invalid Main Image URL. "
                "Use a URL beginning with "
                "`http://` or `https://`.",
                ephemeral=True
            )

            return

        self.data.image_url = image_url


        await interaction.response.send_message(
            "✅ Image settings updated.",
            ephemeral=True
        )


# =============================================================
# Footer Modal
# =============================================================

class FooterModal(
    discord.ui.Modal
):

    def __init__(
        self,
        data: EmbedData
    ):

        super().__init__(
            title="Footer Settings"
        )

        self.data = data


        #----------------
        # Footer Text
        #----------------

        self.text_input = discord.ui.TextInput(
            label="Footer Text",
            required=False,
            max_length=2048,
            default=data.footer_text
        )


        #----------------
        # Footer Icon URL
        #----------------

        self.icon_input = discord.ui.TextInput(
            label="Footer Icon URL",
            placeholder="https://example.com/icon.png",
            required=False,
            default=data.footer_icon_url or ""
        )


        self.add_item(
            self.text_input
        )

        self.add_item(
            self.icon_input
        )


    async def on_submit(
        self,
        interaction: discord.Interaction
    ):


        #----------------
        # Footer Text
        #----------------

        self.data.footer_text = (
            self.text_input.value.strip()
        )


        #----------------
        # Footer Icon URL
        #----------------

        icon_url = clean_url(
            self.icon_input.value
        )

        if (
            self.icon_input.value.strip()
            and not icon_url
        ):

            await interaction.response.send_message(
                "❌ Invalid Footer Icon URL. "
                "Use a URL beginning with "
                "`http://` or `https://`.",
                ephemeral=True
            )

            return

        self.data.footer_icon_url = icon_url


        await interaction.response.send_message(
            "✅ Footer settings updated.",
            ephemeral=True
        )


# =============================================================
# Setup
# =============================================================

async def setup(
    bot: commands.Bot
):

    await bot.add_cog(
        EmbedBuilder(bot)
    )
