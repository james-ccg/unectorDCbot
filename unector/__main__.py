import asyncio
import logging

from unector.bot import create_bot
from unector.config import Settings
from unector.webpanel import start_panel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

async def main() -> None:
    settings = Settings.from_env()
    bot = create_bot(settings)
    async with bot:
        panel_runner = await start_panel(bot)
        try:
            await bot.start(settings.discord_token)
        finally:
            if panel_runner is not None:
                await panel_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
