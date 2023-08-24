# this code is ugly and needs to be reworked eventually, but for now... it works™️

import asyncio
import datetime
import discord
import urllib.parse
import colorsys

import random
from discord.ext import commands, tasks

from utils import constants

from bot import Bot


def _get_range(x: int, aperture: int) -> list:
    return [n % 360 for n in range(x - aperture, x + aperture)]


def _get_degree(initial: float, aperture: int = 20):
    exclusion_range = _get_range(int(initial * 360), aperture=aperture)

    degrees = random.uniform(0, 1) * 360

    while int(degrees) in exclusion_range:
        degrees = random.uniform(0, 1) * 360

    return degrees / 360


def random_color(previous_color: discord.Color | None = None):
    if previous_color is None:
        previous_color = discord.Color.random()

    prev_h = colorsys.rgb_to_hsv(previous_color.r / 255, previous_color.g / 255, previous_color.b / 255)
    return discord.Color.from_hsv(_get_degree(prev_h[0], aperture=20), random.uniform(0.8, 1), random.uniform(0.8, 1))


def get_complementary_color(color):
    color = color[1:]
    color = int(color, 16)
    comp_color = 0xFFFFFF ^ color
    comp_color = "#%06X" % comp_color
    return comp_color


color = discord.Color.random()
embeds = []
for _ in range(0, 10):
    color = random_color(color)
    embeds.append(discord.Embed(color=color, title=f"{color}"))


async def do_cotd(bot: Bot):
    previous_num = await bot.pool.fetchval("SELECT color_int FROM cotd ORDER BY added_at DESC LIMIT 1")
    previous = discord.Color(int(previous_num)) if previous_num else None
    color = random_color(previous_color=previous)

    guild = bot.get_guild(constants.MAIN_GUILD)

    if not guild:
        return

    for role_id in constants.COTD_ROLES:
        role = guild.get_role(role_id)
        if role is not None:
            await role.edit(color=color)

    log_channel = guild.get_channel(constants.COTD_CHANNEL)

    embed = discord.Embed(color=color)
    embed.set_author(icon_url="https://imgur.com/izRBtg9", name="Color of the Day")
    q = "'"
    embed.set_image(
        url=f"https://fakeimg.pl/1200x500/{str(color)[1:]}/{get_complementary_color(str(color))[1:]}/"
        f'?text={urllib.parse.quote(f"Today{q}s color is {color}")}'
    )

    await log_channel.send(embed=embed)  # type: ignore  # I want this to raise errors if it fails.
    await bot.pool.execute("INSERT INTO cotd(color_int, added_at) VALUES ($1, $2)", color.value, discord.utils.utcnow())
    return color


class daily_color(commands.Cog):
    """🎨 A role that changes color every day."""

    def __init__(self, bot: Bot):
        self.bot: Bot = bot

        self.remove_newcomers_role.start()
        self.update_cotd_role.start()

    def cog_unload(self):
        self.update_cotd_role.cancel()
        self.remove_newcomers_role.cancel()

    @tasks.loop(time=[datetime.time(hour=i) for i in range(24)])
    async def update_cotd_role(self):
        await do_cotd(self.bot)

    @tasks.loop(minutes=15)
    async def remove_newcomers_role(self):
        guild = self.bot.get_guild(constants.MAIN_GUILD)
        if not guild:
            return

        role = guild.get_role(constants.NEWCOMERS_ROLE)
        if not role:
            return

        for members in role.members:
            date = members.joined_at or discord.utils.utcnow()
            now = discord.utils.utcnow()
            diff = now - date
            hours = diff.total_seconds() / 60 / 60
            if hours >= 336:
                await members.remove_roles(role)
            await asyncio.sleep(5)

    @remove_newcomers_role.before_loop
    async def wait_until_bot_ready(self):
        await self.bot.wait_until_ready()


async def setup(bot: Bot):
    await bot.add_cog(daily_color(bot))
