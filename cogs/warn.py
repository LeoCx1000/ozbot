import asyncio

import discord
from discord.ext import commands

import constants


class Events(commands.Cog):
    """events only, not much."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.bot:
            return

        # skyblock
        if (
            before.status is discord.Status.online
            and after.status is discord.Status.offline
            and before.id == 755309062555435070
        ):
            print("Skyblock went offline")
            await asyncio.sleep(120)
            print("checking...")
            user = self.bot.get_guild(706624339595886683).get_member(755309062555435070)
            if user.status == discord.Status.online:
                return
            else:
                await self.bot.get_channel(799741426886901850).send(
                    "Skyblock has been offline for 2 minutes, y'all might want to check on that!"
                )
                await self.bot.get_channel(755309358967029801).send(
                    "It seems like the server went down! I've notified the staff about it. They'll fix it soon"
                )
                print("Skyblock is still offline")

        # creative
        if (
            before.status is discord.Status.online
            and after.status is discord.Status.offline
            and before.id == 764623648132300811
        ):
            print("Creative went offline")
            await asyncio.sleep(120)
            print("checking...")
            user = self.bot.get_guild(706624339595886683).get_member(764623648132300811)
            if user.status == discord.Status.online:
                return
            else:
                await self.bot.get_channel(799741426886901850).send(
                    "Creative has been offline for 2 minutes, y'all might want to check on that!"
                )
                await self.bot.get_channel(764624072994062367).send(
                    "It seems like the server went down! I've notified the staff about it. They'll fix it soon"
                )
                print("Creative is still offline")

        # lobby
        if (
            before.status is discord.Status.online
            and after.status is discord.Status.offline
            and before.id == 755311461332418610
        ):
            print("Lobby went offline")
            await asyncio.sleep(120)
            print("checking...")
            user = self.bot.get_guild(706624339595886683).get_member(755311461332418610)
            if user.status == discord.Status.online:
                return
            else:
                await self.bot.get_channel(799741426886901850).send(
                    "Lobby has been offline for 2 minutes, y'all might want to check on that!"
                )
                await self.bot.get_channel(755311693042548806).send(
                    "It seems like the server went down! I've notified the staff about it. They'll fix it soon"
                )
                print("Lobby is still offline")

                ##survival
        if (
            before.status is discord.Status.online
            and after.status is discord.Status.offline
            and before.id == 799749818062077962
        ):
            print("survival went offline")
            await asyncio.sleep(120)
            print("checking...")
            user = self.bot.get_guild(706624339595886683).get_member(799749818062077962)
            if user.status == discord.Status.online:
                return
            else:
                await self.bot.get_channel(799741426886901850).send(
                    "Survival has been offline for 2 minutes, y'all might want to check on that!"
                )
                await self.bot.get_channel(799483071069945866).send(
                    "It seems like the server went down! I've notified the staff about it. They'll fix it soon"
                )
                print("Survival is still offline")


async def setup(bot):
    await bot.add_cog(Events(bot))
