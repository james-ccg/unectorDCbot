"""Small password-protected local publishing panel for Unector."""
from __future__ import annotations

import hmac
import os
from html import escape

from aiohttp import web
import discord
from discord.ext import commands


PAGE = '''<!doctype html><html lang="uz"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Unector • Publisher</title>
<style>body{margin:0;background:#0b1020;color:#e8ecf5;font:16px system-ui}main{max-width:850px;margin:36px auto;padding:24px}h1{margin-bottom:4px}.muted{color:#9aa6bd}form{background:#141c30;border:1px solid #28344d;border-radius:18px;padding:22px;display:grid;gap:14px}label{display:grid;gap:7px;color:#cbd5e1}input,select,textarea{box-sizing:border-box;width:100%;padding:12px;border-radius:10px;border:1px solid #35425d;background:#0c1426;color:#fff;font:inherit}textarea{min-height:130px}button{border:0;border-radius:10px;background:#6875f5;color:white;padding:13px;font-weight:700;font-size:16px;cursor:pointer}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.note{padding:12px;background:#202c45;border-radius:10px}@media(max-width:600px){main{margin:8px;padding:14px}.grid{grid-template-columns:1fr}}</style></head><body><main><h1>Unector Publisher</h1><p class="muted">Discord kanallariga qo‘lda post yuborish paneli</p><p class="note">Xavfsizlik: panel standart holatda faqat 127.0.0.1 manzilida ishlaydi. Uni internetga ochiq joylashtirishdan oldin HTTPS va kuchli autentifikatsiya sozlang.</p>
<form method="post" action="/publish"><label>Discord kanali<select name="channel_id" required>{channels}</select></label><label>Post sarlavhasi<input name="title" maxlength="256" placeholder="Masalan: Yangi o‘yin yangiligi" required></label><label>Matn<textarea name="body" maxlength="4000" placeholder="Post matni..." required></textarea></label><div class="grid"><label>Rasm URL (ixtiyoriy)<input name="image_url" type="url" placeholder="https://..."></label><label>Video URL (ixtiyoriy)<input name="video_url" type="url" placeholder="https://..."></label></div><label>Havola (ixtiyoriy)<input name="link_url" type="url" placeholder="https://..."></label><label><span><input style="width:auto" type="checkbox" name="reactions" value="yes" checked> 👍 🔥 ❤️ reaksiyalarini qo‘shish</span></label><button type="submit">Discord’ga yuborish</button></form><p class="muted">Video URL Discord embed sifatida har doim ko‘rinmasligi mumkin; ishonchli video platforma havolasini matnga ham qo‘shing.</p></main></body></html>'''


def _safe_http_url(value: str) -> bool:
    return not value or value.startswith(("https://", "http://"))


def create_app(bot: commands.Bot) -> web.Application:
    user = os.getenv("WEB_PANEL_USER", "").strip()
    password = os.getenv("WEB_PANEL_PASSWORD", "").strip()
    if not user or len(password) < 16:
        raise RuntimeError("Set WEB_PANEL_USER and WEB_PANEL_PASSWORD (at least 16 characters) to enable the panel.")

    @web.middleware
    async def basic_auth(request: web.Request, handler):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Basic "):
            return web.Response(status=401, headers={"WWW-Authenticate": 'Basic realm="Unector Publisher"'})
        import base64
        try:
            supplied_user, supplied_password = base64.b64decode(auth[6:]).decode().split(":", 1)
        except Exception:
            return web.Response(status=401, text="Unauthorized")
        if not (hmac.compare_digest(supplied_user, user) and hmac.compare_digest(supplied_password, password)):
            return web.Response(status=401, text="Unauthorized", headers={"WWW-Authenticate": 'Basic realm="Unector Publisher"'})
        return await handler(request)

    async def index(request: web.Request) -> web.Response:
        guild_id = int(os.getenv("DISCORD_GUILD_ID", "0") or 0)
        guild = bot.get_guild(guild_id) if guild_id else next(iter(bot.guilds), None)
        if guild is None:
            return web.Response(text="Bot hali serverga ulanmagan yoki DISCORD_GUILD_ID noto‘g‘ri.", status=503)
        channels = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages and c.permissions_for(guild.me).embed_links]
        options = "".join(f'<option value="{c.id}">#{escape(c.name)}</option>' for c in channels)
        return web.Response(text=PAGE.replace("{channels}", options), content_type="text/html")

    async def publish(request: web.Request) -> web.Response:
        form = await request.post()
        try:
            channel_id = int(form.get("channel_id", "0"))
        except ValueError:
            return web.Response(text="Kanal ID noto‘g‘ri", status=400)
        channel = bot.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return web.Response(text="Kanal topilmadi yoki matn kanali emas", status=404)
        title = str(form.get("title", "")).strip()[:256]
        body = str(form.get("body", "")).strip()[:4000]
        image_url = str(form.get("image_url", "")).strip()
        video_url = str(form.get("video_url", "")).strip()
        link_url = str(form.get("link_url", "")).strip()
        if not title or not body or not all(_safe_http_url(x) for x in (image_url, video_url, link_url)):
            return web.Response(text="Sarlavha/matn kerak; havolalar http(s) bilan boshlanishi lozim.", status=400)
        embed = discord.Embed(title=title, description=body, color=discord.Color.from_rgb(92, 105, 245))
        if link_url:
            embed.url = link_url
        if image_url:
            embed.set_image(url=image_url)
        if video_url:
            embed.add_field(name="Video", value=f"[Videoni ko‘rish]({video_url})", inline=False)
        embed.set_footer(text="Unector • Community tools")
        message = await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        if form.get("reactions") == "yes":
            for emoji in ("👍", "🔥", "❤️"):
                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    pass
        return web.Response(text=f"Post yuborildi: {message.jump_url}\n\nPanelga qaytish: /", content_type="text/plain")

    app = web.Application(middlewares=[basic_auth], client_max_size=64 * 1024)
    app.router.add_get("/", index)
    app.router.add_post("/publish", publish)
    return app


async def start_panel(bot: commands.Bot) -> web.AppRunner | None:
    if os.getenv("WEB_PANEL_ENABLED", "0") != "1":
        return None
    app = create_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    host = os.getenv("WEB_PANEL_HOST", "127.0.0.1")
    port = int(os.getenv("WEB_PANEL_PORT", "8787"))
    site = web.TCPSite(runner, host, port)
    await site.start()
    return runner
