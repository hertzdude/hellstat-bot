import discord
from discord.ext import commands
from services.voice_tracker import VoiceTracker


class VoiceEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, tracker: VoiceTracker):
        self.bot = bot
        self.tracker = tracker

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if member.bot:
                        continue
                    self.tracker.on_join(guild.id, member.id)
        try:
            await self.bot.tree.sync()
        except Exception as e:
            print("Slash sync error:", e)
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if member.bot:
            return
        gid = member.guild.id

        # join
        if before.channel is None and after.channel is not None:
            self.tracker.on_join(gid, member.id)
            return

        # leave
        if before.channel is not None and after.channel is None:
            self.tracker.on_leave(gid, member.id)
            return


async def setup(bot: commands.Bot):
    tracker: VoiceTracker = bot.tracker
    await bot.add_cog(VoiceEvents(bot, tracker))
