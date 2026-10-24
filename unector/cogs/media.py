import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp
import discord
from discord.ext import commands, tasks

from unector.config import Settings
from unector.database import Database
from unector.services.media_api import MediaAPI

log = logging.getLogger(__name__)

class Media(commands.Cog):
    def __init__(self, bot: commands.Bot, settings: Settings, database: Database) -> None:
        self.bot = bot
        self.settings = settings
        self.database = database
        self.session: aiohttp.ClientSession | None = None
        self.api: MediaAPI | None = None

    async def cog_load(self) -> None:
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "UnectorDiscordBot/0.1"},
            timeout=aiohttp.ClientTimeout(total=15),
        )
        self.api = MediaAPI(self.session)
        self.poll_media.start()

    async def cog_unload(self) -> None:
        self.poll_media.cancel()
        if self.session is not None:
            await self.session.close()

    @tasks.loop(minutes=30)
    async def poll_media(self) -> None:
        if self.api is None:
            return
        if self.settings.game_news_channel_id is None:
            log.info("GAME_NEWS_CHANNEL_ID is unset; skipping automatic media posting.")
            return
        channel = self.bot.get_channel(self.settings.game_news_channel_id)
        if not isinstance(channel, (discord.TextChannel, discord.Thread, discord.ForumChannel, discord.VoiceChannel)):
            fetched = await self.bot.fetch_channel(self.settings.game_news_channel_id)
            channel = fetched
        if not isinstance(channel, discord.TextChannel):
            log.error("Configured media channel ID is not a text or announcement channel.")
            return

        try:
            giveaways = await self.api.get_giveaways()
            for item in reversed(giveaways[:10]):
                await self._publish_giveaway(channel, item)
            for app_id in self.settings.steam_app_ids:
                news = await self.api.get_steam_news(app_id)
                for item in reversed(news[:5]):
                    await self._publish_steam_news(channel, app_id, item)
        except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
            log.warning("Media poll failed; will retry next cycle: %s", exc)
        except discord.DiscordException:
            log.exception("Discord rejected a media post; will retry on a future cycle.")

    @poll_media.before_loop
    async def before_poll_media(self) -> None:
        await self.bot.wait_until_ready()
        self.poll_media.change_interval(minutes=self.settings.media_poll_minutes)

    async def _publish_giveaway(self, channel: discord.TextChannel, item: dict[str, Any]) -> None:
        item_id = str(item.get("id", "")).strip()
        if not item_id or await self.database.has_published("gamerpower", item_id):
            return
        title = str(item.get("title") or "Free game giveaway")[:256]
        url = str(item.get("open_giveaway_url") or "https://www.gamerpower.com")
        platform = str(item.get("platforms") or "Not specified")[:1024]
        description = str(item.get("description") or "Open the giveaway page for details.")[:3500]
        embed = discord.Embed(title=title, url=url, description=description, color=discord.Color.green())
        embed.add_field(name="Platform", value=platform, inline=True)
        embed.add_field(
            name="Source",
            value="[GamerPower.com](https://www.gamerpower.com/)",
            inline=True,
        )
        image_url = str(item.get("image") or item.get("thumbnail") or "").strip()
        if image_url.startswith(("https://", "http://")):
            embed.set_image(url=image_url)
        worth = str(item.get("worth") or "").strip()
        if worth and worth.lower() not in {"n/a", "na", "0"}:
            embed.add_field(name="Value", value=worth[:100], inline=True)
        giveaway_type = str(item.get("type") or "").strip()
        if giveaway_type:
            embed.add_field(name="Type", value=giveaway_type[:100], inline=True)
        end_date = str(item.get("end_date") or "").strip()
        if end_date:
            embed.add_field(name="Ends", value=end_date[:100], inline=True)
        await self._send_post(channel, embed, f"gamerpower:{item_id}")
        await self.database.mark_published("gamerpower", item_id)

    async def _publish_steam_news(
        self,
        channel: discord.TextChannel,
        app_id: int,
        item: dict[str, Any],
    ) -> None:
        item_id = str(item.get("gid") or "").strip()
        if not item_id or await self.database.has_published("steam", item_id):
            return
        title = str(item.get("title") or "Steam news")[:256]
        url = str(item.get("url") or "https://store.steampowered.com/")
        raw = str(item.get("contents") or "").replace("[", "").replace("]", "")
        description = " ".join(raw.split())[:3500] or "Open the article to read the full update."
        embed = discord.Embed(title=title, url=url, description=description, color=discord.Color.blurple())
        embed.add_field(name="Steam App ID", value=str(app_id), inline=True)
        image_url = str(item.get("url") or "").strip()
        # Steam news often has an image in the HTML contents; extract only a safe URL.
        import re
        raw_html = str(item.get("contents") or "")
        match = re.search(r'<img[^>]+src=[\"\'](https?://[^\"\']+)', raw_html, re.IGNORECASE)
        if match:
            embed.set_image(url=match.group(1)[:1000])
        timestamp = item.get("date")
        if isinstance(timestamp, (int, float)):
            embed.timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        await self._send_post(channel, embed, f"steam:{item_id}")
        await self.database.mark_published("steam", item_id)

    async def _send_post(self, channel: discord.TextChannel, embed: discord.Embed, key: str) -> None:
        content = ""
        role_id = self.settings.game_news_role_id
        allowed_mentions = discord.AllowedMentions.none()
        if role_id:
            role = channel.guild.get_role(role_id)
            if role is not None:
                content = role.mention
                allowed_mentions = discord.AllowedMentions(roles=True, users=False, everyone=False)
        message = await channel.send(content=content, embed=embed, allowed_mentions=allowed_mentions)
        # Add lightweight reactions to invite interaction; failures must not block publishing.
        for emoji in ("👍", "🔥", "❤️"):
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException as exc:
                log.debug("Could not add reaction %s to %s: %s", emoji, key, exc)
        try:
            thread = await message.create_thread(name=f"Discussion: {embed.title}"[:100])
            await thread.send(
                f"💬 **Muhokama / Discussion**\n"
                f"Post: {message.jump_url}\n"
                "Fikrlaringizni shu yerda yozing. / Share your thoughts here."
            )
        except discord.HTTPException as exc:
            log.info("Could not create/populate thread for %s: %s", key, exc)

async def setup(bot: commands.Bot) -> None:
    settings: Settings = bot.settings  # type: ignore[attr-defined]
    database: Database = bot.database  # type: ignore[attr-defined]
    await bot.add_cog(Media(bot, settings, database))
