import os
from logging import getLogger
import asyncio
import aiohttp

from dotenv import load_dotenv
import asyncpg
import discord
from discord.ext import commands

from utils.error_manager import ErrorManager

from pkgutil import iter_modules

EXTENSIONS = [module.name for module in iter_modules(["cogs"], f"cogs.")]

log = getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, pool: asyncpg.Pool, session: aiohttp.ClientSession):
        super().__init__(
            command_prefix=os.environ["PREFIX"],
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.session = session
        self.pool = pool
        self.error_manager = ErrorManager(
            self,
            webhook_url=os.environ["ERROR_WEBHOOK"],
            session=session,
            hijack_bot_on_error=True,
        )

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
            except Exception as e:
                await self.error_manager.add_error(error=e)

    async def on_ready(self):
        log.info(f"Logged in as {self.user}")


async def main():
    async with (
        asyncpg.create_pool(os.environ["PG_DSN"]) as pool,
        aiohttp.ClientSession() as session,
        Bot(pool, session) as bot,
    ):
        await bot.start(os.environ["TOKEN"])


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
