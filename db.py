import sqlite3

from typing import Optional, List, Tuple


class Store:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self._init_schema()

    def _init_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id  INTEGER NOT NULL,
                start_ts INTEGER NOT NULL,
                end_ts   INTEGER,
                duration_sec INTEGER
            );
            """
        )
        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sessions_guild_user 
            ON sessions(guild_id, user_id);
            """
        )
        self.conn.commit()

    def open_session(self, guild_id: int, user_id: int, start_ts: int) -> None:
        cur = self.conn.execute(
            """SELECT id FROM sessions 
               WHERE guild_id=? AND user_id=? AND end_ts IS NULL
               ORDER BY id DESC LIMIT 1;""",
            (guild_id, user_id),
        )
        if cur.fetchone():
            return
        self.conn.execute(
            """INSERT INTO sessions(guild_id, user_id, start_ts) 
               VALUES (?, ?, ?);""",
            (guild_id, user_id, start_ts),
        )
        self.conn.commit()

    def close_session(self, guild_id: int, user_id: int, end_ts: int) -> None:
        cur = self.conn.execute(
            """SELECT id, start_ts FROM sessions
               WHERE guild_id=? AND user_id=? AND end_ts IS NULL
               ORDER BY id DESC LIMIT 1;""",
            (guild_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            return
        sid, start_ts = row
        duration = max(0, end_ts - start_ts)
        self.conn.execute(
            """UPDATE sessions SET end_ts=?, duration_sec=? WHERE id=?;""",
            (end_ts, duration, sid),
        )
        self.conn.commit()

    def sum_duration(self, guild_id: int, user_id: int, since_ts: Optional[int]) -> int:
        params = [guild_id, user_id]
        where = "guild_id=? AND user_id=?"
        if since_ts is not None:
            where += " AND start_ts>=?"
            params.append(since_ts)

        cur = self.conn.execute(
            f"""SELECT COALESCE(SUM(duration_sec),0) FROM sessions
                WHERE {where} AND end_ts IS NOT NULL;""",
            tuple(params),
        )
        total = cur.fetchone()[0] or 0

        cur = self.conn.execute(
            f"""SELECT start_ts FROM sessions
                WHERE {where} AND end_ts IS NULL
                ORDER BY id DESC LIMIT 1;""",
            tuple(params),
        )
        row = cur.fetchone()
        if row:
            import time as _t
            total += max(0, int(_t.time()) - row[0])
        return int(total)

    def leaderboard(self, guild_id: int, since_ts: Optional[int], limit: int = 10) -> List[Tuple[int, int]]:
        params = [guild_id]
        where = "guild_id=?"
        if since_ts is not None:
            where += " AND start_ts>=?"
            params.append(since_ts)

        cur = self.conn.execute(
            f"""
            SELECT user_id, COALESCE(SUM(duration_sec),0) AS total
            FROM sessions
            WHERE {where} AND end_ts IS NOT NULL
            GROUP BY user_id
            """,
            tuple(params),
        )
        totals = {row[0]: int(row[1]) for row in cur.fetchall()}

        cur = self.conn.execute(
            f"""
            SELECT user_id, start_ts
            FROM sessions
            WHERE {where} AND end_ts IS NULL
            """,
            tuple(params),
        )
        import time as _t
        now = int(_t.time())
        for uid, start_ts in cur.fetchall():
            totals[uid] = totals.get(uid, 0) + max(0, now - start_ts)

        return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:limit]
