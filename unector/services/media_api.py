from typing import Any

import aiohttp

GAMERPOWER_URL = "https://www.gamerpower.com/api/giveaways"
STEAM_NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"

class MediaAPI:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def get_giveaways(self) -> list[dict[str, Any]]:
        async with self.session.get(
            GAMERPOWER_URL,
            params={"type": "game", "sort-by": "date"},
            timeout=aiohttp.ClientTimeout(total=12),
        ) as response:
            if response.status == 201:
                return []
            response.raise_for_status()
            data = await response.json(content_type=None)
            if not isinstance(data, list):
                return []
            return [item for item in data if isinstance(item, dict)]

    async def get_steam_news(self, app_id: int) -> list[dict[str, Any]]:
        async with self.session.get(
            STEAM_NEWS_URL,
            params={"appid": app_id, "count": 5, "maxlength": 500, "format": "json"},
            timeout=aiohttp.ClientTimeout(total=12),
        ) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)
        appnews = data.get("appnews", {}) if isinstance(data, dict) else {}
        news_items = appnews.get("newsitems", []) if isinstance(appnews, dict) else []
        if not isinstance(news_items, list):
            return []
        return [item for item in news_items if isinstance(item, dict)]
