import datetime
import io
import logging
import os
import asyncio
import traceback
from collections import defaultdict
from typing import List, Optional, Union, Any

import aiohttp
import asyncpg
import discord
from discord.ext import commands
from discord.ext.commands.errors import (
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    NoEntryPointError,
)
from dotenv import load_dotenv

import helpers

initial_extensions = ("jishaku",)

load_dotenv()

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)-15s] %(message)s")

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_USE_BRAILLE_J"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
PG_CRED = {
    "user": f"{os.getenv('PSQL_USER')}",
    "password": f"{os.getenv('PSQL_PASSWORD')}",
    "database": f"{os.getenv('PSQL_DB')}",
    "host": f"{os.getenv('PSQL_HOST')}",
}
target_type = Union[
    discord.Member,
    discord.User,
    discord.PartialEmoji,
    discord.Guild,
    discord.Invite,
    str,
]


class Ozbot(commands.Bot):
    PRE: tuple = ("!",)

    def __init__(self, pool: asyncpg.Pool, session: aiohttp.ClientSession) -> None:
        intents = discord.Intents.all()
        # noinspection PyDunderSlots,PyUnresolvedReferences
        intents.typing = False

        super().__init__(
            intents=intents,
            command_prefix=self.get_pre,
            case_insensitive=True,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="over OZ"
            ),
            strip_after_prefix=True,
        )

        self.owner_id = 349373972103561218

        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        # Bot based stuff
        self.uptime = datetime.datetime.utcnow()
        self.last_rall = datetime.datetime.utcnow()
        self.allowed_mentions = discord.AllowedMentions.none()
        self.session: aiohttp.ClientSession = session

        # Cache stuff
        self.prefixes = {}

        self.db: asyncpg.Pool[asyncpg.Record] = pool

    async def _load_extension(self, name: str) -> None:
        try:
            await self.load_extension(name)
        except (
            ExtensionNotFound,
            ExtensionAlreadyLoaded,
            NoEntryPointError,
            ExtensionFailed,
        ):
            traceback.print_exc()
            print()  # Empty line

    async def dynamic_load_cogs(self) -> None:
        for filename in os.listdir(f"cogs"):
            if filename.endswith(".py"):
                cog = filename[:-3]
                if cog not in ["moderation", "whitelist", "vcban"]:
                    logging.info(f"Trying to load cog: {cog}")
                    await self._load_extension(f"cogs.{cog}")
        for cog in ["moderation", "whitelist", "vcban"]:
            await self.wait_until_ready()
            logging.info(f"Trying to load cog: {cog}")
            await self._load_extension(f"cogs.{cog}")
        logging.info("Loading cogs done.")
        self.dispatch("restart_complete")

    async def get_pre(
        self, bot, message: discord.Message, raw_prefix: Optional[bool] = False
    ):
        if not message:
            return (
                commands.when_mentioned_or(*self.PRE)(bot, message)
                if not raw_prefix
                else self.PRE
            )
        if not message.guild:
            return (
                commands.when_mentioned_or(*self.PRE)(bot, message)
                if not raw_prefix
                else self.PRE
            )
        try:
            prefix = self.prefixes[message.guild.id]
        except KeyError:
            prefix = [
                x["prefix"]
                for x in await bot.db.fetch(
                    "SELECT prefix FROM pre WHERE guild_id = $1", message.guild.id
                )
            ] or self.PRE
            self.prefixes[message.guild.id] = prefix
        return (
            commands.when_mentioned_or(*prefix)(bot, message)
            if not raw_prefix
            else prefix
        )

    async def on_ready(self) -> None:
        e = "\033[0m"
        s = "\033[42m"
        logging.info("======[ BOT ONLINE! ]=======")
        logging.info("\033[42mLogged in as " + self.user.name + "\033[0m")

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        traceback_string = traceback.format_exc()
        logging.error("Error in event %s", event_method)
        await self.wait_until_ready()
        error_channel: discord.TextChannel = self.get_channel(880181130408636456)  # type: ignore
        to_send = (
            f"```yaml\nAn error occurred in an {event_method} event``````py"
            f"\n{traceback_string}\n```"
        )
        if len(to_send) < 2000:
            await error_channel.send(to_send)
        else:
            await error_channel.send(
                f"```yaml\nAn error occurred in an {event_method} event``````py",
                file=discord.File(
                    io.BytesIO(traceback_string.encode()), filename="traceback.py"
                ),
            )

    async def setup_hook(self):
        for ext in initial_extensions:
            await self._load_extension(ext)
        self.loop.create_task(self.populate_cache())
        self.loop.create_task(self.dynamic_load_cogs())

    async def on_interaction(self, interaction: discord.Interaction):
        return

    async def populate_cache(self):
        _temp_prefixes = defaultdict(list)
        for x in await self.db.fetch("SELECT * FROM pre"):
            _temp_prefixes[x["guild_id"]].append(x["prefix"] or self.PRE)
        self.prefixes = dict(_temp_prefixes)
        logging.info("All cache populated successfully")

        async def _populate_guild_cache():
            await self.wait_until_ready()
            for guild in self.guilds:
                try:
                    self.prefixes[guild.id]
                except KeyError:
                    self.prefixes[guild.id] = self.PRE

        self.loop.create_task(_populate_guild_cache())
        self.dispatch("cache_ready")

    async def start(self, *args, **kwargs):
        self.session = aiohttp.ClientSession()
        await super().start(*args, **kwargs)

    async def close(self):
        await self.db.close()
        await self.session.close()
        await super().close()


if __name__ == "__main__":

    async def startup():
        TOKEN = os.getenv("DISCORD_TOKEN")
        async with asyncpg.create_pool(
            **PG_CRED
        ) as pool, aiohttp.ClientSession() as session, Ozbot(pool, session) as bot:

            @bot.check
            async def oz_only(ctx: commands.Context) -> bool:
                if await bot.is_owner(ctx.author):
                    return True
                if not ctx.guild:
                    raise helpers.NotOz
                if ctx.guild.id != 706624339595886683:
                    raise helpers.NotOz
                return True

            await bot.start(TOKEN)

    asyncio.run(startup())
