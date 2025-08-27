from datetime import datetime, timedelta, timezone
import discord
from discord import app_commands
from discord.ext import commands
from services.voice_tracker import VoiceTracker
from utils.timefmt import fmt_duration


class CoreCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, tracker: VoiceTracker):
        self.bot = bot
        self.tracker = tracker

    @app_commands.command(name="ping", description="Проверка бота")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="me")
    async def me(self, interaction: discord.Interaction, days: int | None = None):
        await interaction.response.defer(ephemeral=True)
        since_ts = None
        if days is not None:
            if not (1 <= days <= 3650):
                await interaction.followup.send("Укажи days в диапазоне 1–3650.", ephemeral=True)
                return
            since_ts = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
        total = self.tracker.total_for_user(interaction.guild_id, interaction.user.id, since_ts)
        period = f"за {days} дн" if days else "за всё время"
        await interaction.followup.send(
            f"⏱️ {interaction.user.mention}, ваше время в войсах {period}: **{fmt_duration(total)}**",
            ephemeral=True
        )

    @app_commands.command(name="leaderboard")
    async def top(self, interaction: discord.Interaction, days: int | None = None, limit: int = 10):
        await interaction.response.defer()
        if not (1 <= limit <= 50):
            await interaction.followup.send("limit должен быть от 1 до 50.")
            return
        since_ts = None
        if days is not None:
            if not (1 <= days <= 3650):
                await interaction.followup.send("days должен быть от 1 до 3650.")
                return
            since_ts = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())

        lb = self.tracker.top(interaction.guild_id, since_ts, limit=limit)
        if not lb:
            await interaction.followup.send("Пока нет данных для топа")
            return

        lines = []
        for i, (user_id, seconds) in enumerate(lb, start=1):
            user = interaction.guild.get_member(user_id)
            if user is None:
                try:
                    user = await interaction.guild.fetch_member(user_id)
                except discord.NotFound:
                    user = None
            name = user.display_name if user else f"User {user_id}"
            lines.append(f"**{i}.** {name} — {fmt_duration(seconds)}")

        title = f"🏆 Топ по времени {'за ' + str(days) + ' дн.' if days else 'за всё время'}"
        await interaction.followup.send(f"{title}\n" + "\n".join(lines))


async def setup(bot: commands.Bot):
    tracker: VoiceTracker = bot.tracker
    await bot.add_cog(CoreCommands(bot, tracker))
