import time
from typing import Optional, List, Tuple
from db import Store


def now_ts() -> int:
    return int(time.time())


class VoiceTracker:
    def __init__(self, store: Store):
        self.store = store

    def on_join(self, guild_id: int, user_id: int) -> None:
        self.store.open_session(guild_id, user_id, now_ts())

    def on_leave(self, guild_id: int, user_id: int) -> None:
        self.store.close_session(guild_id, user_id, now_ts())

    def total_for_user(self, guild_id: int, user_id: int, since_ts: Optional[int]) -> int:
        return self.store.sum_duration(guild_id, user_id, since_ts)

    def top(self, guild_id: int, since_ts: Optional[int], limit: int = 10) -> List[Tuple[int, int]]:
        return self.store.leaderboard(guild_id, since_ts, limit)
