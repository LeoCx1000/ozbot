import discord
from discord.ext import commands

from utils import constants
from bot import Bot


class Welcome(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != constants.MAIN_GUILD:
            return
        if not member.bot:
            channel = self.bot.get_channel(constants.WELCOME_CHANNEL)
            if isinstance(channel, discord.abc.Messageable):
                await channel.send(
                    f"{member.mention}, Welcome to {member.guild.name}! Make sure to read and agree "
                    f"to the <#{constants.RULES_CHANNEL}> to get access to the rest of {member.guild.name}.",
                    allowed_mentions=discord.AllowedMentions.all(),
                )

        extra = ""
        if member.global_name and str(member) != member.global_name:
            extra = f" ({member.global_name})"

        channel = self.bot.get_channel(constants.JOIN_LOGS_CHANNEL)
        if isinstance(channel, discord.abc.Messageable):
            await channel.send(f"""{constants.JOINED_SERVER} **{member}{extra}** joined **{member.guild.name}**!""")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != constants.MAIN_GUILD:
            return

        extra = ""
        if member.global_name and str(member) != member.global_name:
            extra = f" ({member.global_name})"

        channel = self.bot.get_channel(constants.JOIN_LOGS_CHANNEL)
        if isinstance(channel, discord.abc.Messageable):
            await channel.send(f"""{constants.LEFT_SERVER} **{member}{extra}** left **{member.guild.name}**!""")


async def setup(bot: Bot):
    await bot.add_cog(Welcome(bot))
