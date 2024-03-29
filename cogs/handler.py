import io
import logging
import re
import traceback

import asyncpg
import discord
import jishaku.paginators
from discord.ext import commands
from discord.ext.commands import BucketType

import helpers
from bot import Ozbot

class handler(commands.Cog):
    """🆘 Handle them errors 👀"""

    def __init__(self, bot: Ozbot):
        self.bot = bot
        self.error_channel = 880181130408636456

    @commands.Cog.listener("on_command_error")
    async def error_handler(self, ctx: commands.Context, error: Exception):
        error = getattr(error, "original", error)
        ignored = (commands.CommandNotFound, commands.DisabledCommand)
        if isinstance(error, ignored):
            return
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CheckAnyFailure):
            for e in error.errors:
                if not isinstance(error, commands.NotOwner):
                    error = e
                    break

        if isinstance(error, commands.BadUnionArgument):
            if error.errors:
                error = error.errors[0]

        embed = discord.Embed(color=0xD7342A)
        embed.set_author(
            name="Missing permissions!", icon_url="https://i.imgur.com/OAmzSGF.png"
        )

        if isinstance(error, commands.NotOwner):
            return await ctx.send(
                f"you must own `{ctx.me.display_name}` to use `{ctx.command}`"
            )

        if isinstance(error, commands.TooManyArguments):
            return await ctx.send(f"Too many arguments passed to the command!")

        if isinstance(error, commands.MissingPermissions):
            text = f"You're missing the following permissions: \n**{', '.join(error.missing_permissions)}**"
            embed.description = text
            try:
                return await ctx.send(embed=embed)
            except discord.Forbidden:
                try:
                    return await ctx.send(text)
                except discord.Forbidden:
                    pass
                finally:
                    return

        if isinstance(error, commands.BotMissingPermissions):
            text = f"I'm missing the following permissions: \n**{', '.join(error.missing_permissions)}**"
            try:
                embed.description = text
                await ctx.send(embed=embed)
            except discord.Forbidden:
                await ctx.send(text)
            finally:
                return

        elif isinstance(error, commands.MissingRequiredArgument):
            missing = f"{str(error.param).split(':')[0]}"
            command = f"{ctx.clean_prefix}{ctx.command} {ctx.command.signature}"
            separator = " " * (len(command.split(missing)[0]) - 1)
            indicator = "^" * (len(missing) + 2)

            logging.info(f"`{separator}`  `{indicator}`")
            logging.info(error.param)

            return await ctx.send(
                f"```{command}\n{separator}{indicator}\n{missing} is a required argument that is missing.\n```"
            )

        elif isinstance(error, commands.errors.PartialEmojiConversionFailure):
            return await ctx.send(f"`{error.argument}` is not a valid Custom Emoji")

        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(
                color=0xD7342A,
                description=f"Please try again in {round(error.retry_after, 2)} seconds",
            )
            embed.set_author(
                name="Command is on cooldown!",
                icon_url="https://i.imgur.com/izRBtg9.png",
            )

            if error.type == BucketType.default:
                per = ""
            elif error.type == BucketType.user:
                per = "per user"
            elif error.type == BucketType.guild:
                per = "per server"
            elif error.type == BucketType.channel:
                per = "per channel"
            elif error.type == BucketType.member:
                per = "per member"
            elif error.type == BucketType.category:
                per = "per category"
            elif error.type == BucketType.role:
                per = "per role"
            else:
                per = ""

            embed.set_footer(
                text=f"cooldown: {error.cooldown.rate} per {error.cooldown.per}s {per}"
            )
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            embed = discord.Embed(
                color=0xD7342A,
                description=f"Please try again once you are done running the command",
            )
            embed.set_author(
                name="Command is alrady running!",
                icon_url="https://i.imgur.com/izRBtg9.png",
            )

            if error.per == BucketType.default:
                per = ""
            elif error.per == BucketType.user:
                per = "per user"
            elif error.per == BucketType.guild:
                per = "per server"
            elif error.per == BucketType.channel:
                per = "per channel"
            elif error.per == BucketType.member:
                per = "per member"
            elif error.per == BucketType.category:
                per = "per category"
            elif error.per == BucketType.role:
                per = "per role"
            else:
                per = ""

            embed.set_footer(text=f"limit is {error.number} command(s) running {per}")
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.MemberNotFound):
            return await ctx.send(f"I couldn't find `{error.argument}` in this server")

        elif isinstance(error, commands.errors.UserNotFound):
            return await ctx.send(
                f"I've searched far and wide, but `{error.argument}` doesn't seem to be a member discord user..."
            )

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(str(error) or "Bad argument given!")

        elif isinstance(error, helpers.NotOz):
            return await ctx.send("Commands are restricted to OZ!")

        await self.bot.errors.add_error(error=error, ctx=ctx)

async def setup(bot):
    await bot.add_cog(handler(bot))
