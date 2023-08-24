import asyncio
import discord
from discord.ext import commands

from bot import Bot
from utils import constants


class text(commands.Cog):
    """📝 Text commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=["s", "send", "foo"])
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, *, msg):
        """Says a message as the bot."""
        await ctx.message.delete()
        if ctx.message.reference and isinstance((reply := ctx.message.reference.resolved), discord.Message):
            await reply.reply(msg)
        else:
            await ctx.send(msg)

    @commands.command(aliases=["a", "an"])
    @commands.has_guild_permissions(administrator=True)
    async def announce(self, ctx: commands.Context, channels: commands.Greedy[discord.abc.GuildChannel], *, msg: str = ""):
        """Sends a message to one or more channels as the bot."""
        assert isinstance(ctx.author, discord.Member)

        if ctx.message.reference and isinstance((reply := ctx.message.reference.resolved), discord.Message):
            msg = reply.content

        if not msg:
            raise commands.BadArgument(f"No message was given. Use `!announce [channels...] <message content>`")

        failed, success = [], []

        for channel in channels:
            if isinstance(channel, discord.abc.Messageable):
                try:
                    await channel.send(msg)
                except discord.HTTPException:
                    failed.append(channel)
                success.append(channel)
            else:
                failed.append(channel)

        if success:
            message = f"```\n{msg}\nSent to {', '.join(c.mention for c in success)}"
        else:
            message = "Message was not sent to any channel."

        if failed:
            message += f"\nFailed to send to {', '.join(c.mention for c in failed)}"

        await ctx.send(message)

    @commands.command(aliases=["e"])
    @commands.has_permissions(manage_messages=True)
    async def edit(self, ctx: commands.Context, *, new: str = "--d"):
        """Edits the message from the bot that you have replied to.

        If no content is passed, then the message will be deleted.
        If `--d` is added at the end then it will also be deleted.
        If `--d` is added at the end, then the embeds of the message will be removed.
        """
        if ctx.message.reference:
            msg = ctx.message.reference.resolved
            assert isinstance(msg, discord.Message)

            try:
                if msg.author == self.bot.user:
                    if new.endswith("--s"):
                        await msg.edit(content=new[:-3] if new[:-3].strip() else msg.content, suppress=True)
                    elif new.endswith("--d"):
                        await msg.delete()
                    else:
                        await msg.edit(content=new)
                    await ctx.message.delete()
            except discord.HTTPException:
                pass

    @commands.Cog.listener("on_thread_create")
    async def pin_thread_starter_message(self, thread: discord.Thread) -> None:
        if thread.parent_id != constants.MARKET_FORUM:
            return

        message = thread.get_partial_message(thread.id)
        try:
            await asyncio.sleep(1)
            await message.pin()
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            await self.bot.error_manager.add_error(error=error.original, ctx=ctx)
            await ctx.send("An unexpected error occurred. This error has been logged.")
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            await ctx.send(str(error))


async def setup(bot: Bot):
    await bot.add_cog(text(bot))
