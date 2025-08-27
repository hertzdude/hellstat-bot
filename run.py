import asyncio
from discord.ext import commands
from config import DISCORD_TOKEN, DB_PATH, INTENTS
from db import Store
from services.voice_tracker import VoiceTracker


EXTENSIONS = [
    "cogs.core_commands",
    "events.voice_events",
]


class VoiceBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = Store(DB_PATH)
        self.tracker = VoiceTracker(self.store)


async def main():
    if not DISCORD_TOKEN:
        raise SystemExit("TOKEN")
    bot = VoiceBot(command_prefix="?", intents=INTENTS)
    async with bot:
        for ext in EXTENSIONS:
            await bot.load_extension(ext)
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
