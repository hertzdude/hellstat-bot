import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = os.getenv("VOICE_TIME_DB", "voice_time.sqlite3")

import discord

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True
INTENTS.voice_states = True
