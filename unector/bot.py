import logging

import discord
from discord.ext import commands

from unector.config import Settings
from unector.database import Database

log = logging.getLogger(__name__)

class UnectorBot(commands.Bot):
    def __init__(self, settings: Settings, database: Database) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = False
        intents.voice_states = True
        intents.message_content = False
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.settings = settings
        self.database = database

    async def setup_hook(self) -> None:
        await self.database.open()
        await self.load_extension("unector.cogs.core")
        await self.load_extension("unector.cogs.media")
        if self.settings.discord_guild_id:
            guild = discord.Object(id=self.settings.discord_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info("Synced slash commands to configured test guild.")
        else:
            await self.tree.sync()
            log.info("Synced global slash commands.")

    async def close(self) -> None:
        await super().close()
        await self.database.close()

def create_bot(settings: Settings) -> UnectorBot:
    return UnectorBot(settings, Database(settings.database_path))
