# Discord Bot Configuration

# =========================
# Discord
# =========================

BOT_TOKEN = ""

# =========================
# Server
# =========================

GUILD_ID = 1545055927986815106

# The Discord user ID of the server owner
SERVER_OWNER_ID = 98607138485575680

# =========================
# Roles
# =========================
ADMIN_ROLE_ID = 1545063208170295316
ROBITS_ROLE_ID = 1545065503800692796
REAL_NINJA_ROLE_ID = 1545062456789962812
CONTENT_CREATOR_ROLE_ID = 1546875246399852605
GAME_DEVELOPER_ROLE_ID = 1546875382853140570
REVIEWER_ROLE_ID = 1546875329828880404
PLAYTESTER_ROLE_ID = 1546875507789013032


# =========================
# Channels
# =========================

# Channel IDs
MOD_LOGS_CHANNEL_ID = 1545226179030814720
WELCOME_CHANNEL_ID = 1545061928945066004
GENERAL_CHANNEL_ID = 1545055929769271378

NEWS_CHANNEL_ID = 1545056196103250071
DEV_LOG_CHANNEL_ID = 1545056171566829648
FAQ_CHANNEL_ID = 1545057266024194160

BUG_REPORTS_CHANNEL_ID = 1545057144221474876
SUPPORT_CHANNEL_ID = 1545058162355474463
SUGGESTIONS_CHANNEL_ID = 1545057099292090428

ROLES_CHANNEL_ID = 1546880569458163822
RULES_CHANNEL_ID = 1545094811097370806
BOT_DUMP_CHAT_CHANNEL_ID = 1545061702524215327
EMBED_BUILDER_CHANNEL_ID = 1545429418497937560

# =========================
# Bot Settings
# =========================

COMMAND_PREFIX = "/"

LOG_FILE = "logs/bot.log"

# =========================
# Embed Builder
# =========================

EMBED_BUILDER_ROLE_IDS = [
    ADMIN_ROLE_ID,
    ROBITS_ROLE_ID
]

EMBED_DESTINATION_CHANNEL_IDS = [
    RULES_CHANNEL_ID,
    GENERAL_CHANNEL_ID,
    NEWS_CHANNEL_ID,
    FAQ_CHANNEL_ID,
    DEV_LOG_CHANNEL_ID,
    BUG_REPORTS_CHANNEL_ID,
    SUPPORT_CHANNEL_ID,
    EMBED_BUILDER_CHANNEL_ID,
    ROLES_CHANNEL_ID
]


# =========================
# Welcome Message
# =========================

WELCOME_TITLE = "A New Ninja Has Arrived!"
WELCOME_COLOR = 0xFFD700
WELCOME_IMAGE_URL = "https://cdn.discordapp.com/attachments/1545228736247635988/1545228780396740730/Faceset.png?ex=6a9b61f2&is=6a9a1072&hm=9db9980b803ffd060a9420a10ba76bd4e8160ba16a2e7f705933c4e06ee65db6&"

WELCOME_MESSAGES = [
    "🥷 A new ninja, {member}, has been spotted! The adventure begins!",
    "🥷 {member} has joined the ranks! Welcome, ninja!",
    "🥷 A new warrior enters the dojo! Welcome, {member}!",
    "🥷 {member} has arrived! Another ninja joins the journey!",
    "🥷 The ranks grow stronger! Welcome, {member}!",
    "🥷 {member} has stepped out of the shadows! Welcome to the server!"
]

# =========================
# Custom Emojis and IDs
# =========================

EMOJIS = {
    "inspector": 1545486633879474227,
    "dark_mage_ninja": 1545486565705252964,
    "water_pot": 1545485909003337848,
    "sword": 1545485781634916392,
    "milk_pot": 1545485876509933618,
    "medipack": 1545485844134240436,
    "light_armor": 1545485947154727004,
    "life_pot": 1545485819622727781,
    "heavy_armor": 1545485980964757555,
    "heart": 1545485728656662668,
    "glaive": 1545485754476793957,
    "empty_pot": 1545485679343964191,
}

# =========================
# Reaction Roles
# =========================

REACTION_ROLE_MESSAGES = {

    # Community Roles
    1546883442703204487: {
        "🎥": CONTENT_CREATOR_ROLE_ID,
        "💻": GAME_DEVELOPER_ROLE_ID,
        "🎮": PLAYTESTER_ROLE_ID,
        EMOJIS["inspector"]: REVIEWER_ROLE_ID
    },

}

# ===========================
# Game Builds Download Links
# ===========================

GAME_WINDOWS_URL = "https://goodwingames.servegame.com/game-builds/RealNinjasKnow/latest/windows/RealNinjasKnow-Windows.zip"
GAME_LINUX_URL = "https://goodwingames.servegame.com/game-builds/RealNinjasKnow/latest/linux/RealNinjasKnow-Linux.zip"
