from pathlib import Path

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS published_items (
    source TEXT NOT NULL,
    item_id TEXT NOT NULL,
    published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source, item_id)
);
"""

class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.connection: aiosqlite.Connection | None = None

    async def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.path)
        await self.connection.execute("PRAGMA journal_mode=WAL;")
        await self.connection.execute(SCHEMA)
        await self.connection.commit()

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def has_published(self, source: str, item_id: str) -> bool:
        if self.connection is None:
            raise RuntimeError("Database is not open.")
        async with self.connection.execute(
            "SELECT 1 FROM published_items WHERE source = ? AND item_id = ?",
            (source, item_id),
        ) as cursor:
            return await cursor.fetchone() is not None

    async def mark_published(self, source: str, item_id: str) -> None:
        if self.connection is None:
            raise RuntimeError("Database is not open.")
        await self.connection.execute(
            "INSERT OR IGNORE INTO published_items(source, item_id) VALUES (?, ?)",
            (source, item_id),
        )
        await self.connection.commit()
