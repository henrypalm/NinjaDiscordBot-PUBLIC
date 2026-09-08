# 🥷 Ninja Bot

A custom Discord bot for the **Real Ninjas Know** community.

Ninja Bot provides server utilities, moderation tools, community features, and integrations designed specifically for the Real Ninjas Know Discord server.

---

## 📋 Features

### 🏷️ Reaction Roles

Reaction roles allow members to identify themselves to the community through roles.

Current community roles include:

* 🎥 **Content Creator**
* 💻 **Game Developer**
* 🎮 **Playtester**
* 🔎 **Reviewer**

Reaction-role messages are configured through `config.py`.

---

### 📊 Polls

Create polls directly through Discord slash commands.

Polls support:

* Multiple choices
* Reaction-based voting
* Configurable poll duration
* Automatic poll closing
* Vote results

---

### 👋 Welcome Messages

Automatically welcomes new members to the server.

Welcome messages can be customized through `config.py`, including:

* Message text
* Embed title
* Embed color
* Welcome image
* Multiple randomized welcome messages

---

### 📝 Embed Builder

Provides tools for creating and sending embeds to approved channels.

Access to the embed builder can be restricted through configured Discord roles.

---

## 📁 Project Structure

```text
ninja-bot/
│
├── bot.py
├── config.py
├── requirements.txt
│
├── modules/
│   ├── __init__.py
│   ├── polls.py
│   ├── reaction_roles.py
│   ├── welcome.py
│   └── embed_builder.py
│
├── logs/
│   └── bot.log
│
└── README.md
```

---

## ⚙️ Requirements

* Python 3.10+
* `discord.py`
* A Discord application/bot
* Discord server with appropriate bot permissions

Install the required Python packages with:

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

Server configuration is stored in:

```text
config.py
```

This includes:

* Bot token
* Server ID
* Role IDs
* Channel IDs
* Custom emoji IDs
* Reaction-role configuration
* Embed builder permissions
* Welcome message configuration
* Game download links

### Example

```python
GUILD_ID = 123456789012345678

ADMIN_ROLE_ID = 123456789012345678
CONTENT_CREATOR_ROLE_ID = 123456789012345678
GAME_DEVELOPER_ROLE_ID = 123456789012345678
```

---

## 🏷️ Reaction Role Configuration

Reaction roles are configured using the `REACTION_ROLE_MESSAGES` dictionary.

Each message ID contains a collection of emoji/role pairs.

Example:

```python
REACTION_ROLE_MESSAGES = {

    123456789012345678: {
        "🎥": CONTENT_CREATOR_ROLE_ID,
        "💻": GAME_DEVELOPER_ROLE_ID,
        "🎮": PLAYTESTER_ROLE_ID,
        EMOJIS["inspector"]: REVIEWER_ROLE_ID
    },

}
```

The bot automatically uses this configuration to:

1. Locate the configured message.
2. Add the configured reactions.
3. Monitor reactions on the message.
4. Assign the corresponding role.
5. Remove the role when the reaction is removed.

---

## 🤖 Bot Permissions

The bot requires the appropriate Discord permissions for the features being used.

At minimum, the bot should have permissions for:

* View Channels
* Send Messages
* Embed Links
* Add Reactions
* Read Message History
* Manage Roles

### Role Hierarchy

For reaction roles, the bot's highest role must be **above the roles it is assigning** in the Discord server's role hierarchy.

For example:

```text
🥷 Ninja Bot
──────────────
🔎 Reviewer
🎮 Playtester
💻 Game Developer
🎥 Content Creator
```

The bot cannot assign or remove roles positioned above its highest role.

---

## 🔐 Security

### Never commit your bot token

The bot token is a secret and should never be uploaded to GitHub or shared publicly.

If a bot token is accidentally exposed, immediately regenerate it through the Discord Developer Portal.

For a public repository, consider keeping secrets in environment variables or a separate configuration file that is excluded from Git.

Example `.gitignore`:

```gitignore
config.py
.env
logs/
__pycache__/
*.pyc
```

---

## 🚀 Running the Bot

Start the bot with:

```bash
python3 bot.py
```

If the bot starts successfully, you should see startup information in the console.

Example:

```text
Bot logged in as Ninja Bot
Loaded module: polls
Loaded module: reaction_roles
Loaded module: welcome
Loaded module: embed_builder
Bot is ready.
```

---

## 🧩 Modules

Ninja Bot is organized into independent Discord Cogs.

This allows individual features to be developed and maintained separately.

### `polls.py`

Handles Discord polls and voting.

### `reaction_roles.py`

Handles reaction-based community roles.

### `welcome.py`

Handles new member welcome messages.

### `embed_builder.py`

Handles creation and publishing of configured embeds.

Additional modules can be added to the `modules/` directory as the bot grows.

---

## 🛠️ Development

When adding a new feature:

1. Create a new module inside `modules/`.
2. Implement the feature as a Discord Cog.
3. Add the module to the bot's extension loader.
4. Add required configuration values to `config.py`.
5. Test the feature in the development server.
6. Update this README if the feature introduces new setup requirements.


---

## 📜 License

Ninja Bot is released under the MIT License.

You are free to use, copy, modify, distribute, and adapt this bot for your own Discord server or project, including commercial projects, provided that the original copyright and license notice are retained.

See the LICENSE file for the complete license.
