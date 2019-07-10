from datetime import datetime, timedelta
import random
import re
import time

import configurations
import googlesheet

import db_user
import discord
from discord.ext import commands


class Users(commands.Cog, name="點數功能"):
    def __init__(self, bot, google_spreadsheet_key):
        self.bot = bot
        self._server_id = int(configurations.key['server'])
        self._newcomer_role_name = configurations.key['newcomer_role']

    @commands.Cog.listener()
    async def on_member_join(self, member):
        server = self.bot.get_guild(self._server_id)
        role = discord.utils.get(server.roles, name=self._newcomer_role_name)
        await member.add_roles(role)
        db_user.add(member.id, member.name)

    @commands.Cog.listener()
    async def on_message(self, message):
        """user takes action in discord server
        Args:
            (Discord.User) discord user class
        """
        discord_user = message.author
        user = db_user.get([discord_user.id])[0]
        if not user:
            db_user.add(discord_user.id, discord_user.name)
        else:
            if user.activity_at < int(time.time()) - (12 * 3600):
                # user can get points for every 12 hours
                db_user.update(user.id, activity_at=time.time(), point=user.point + 1)

    @commands.command(aliases=['points'])
    async def point(self, ctx):
        """查詢自己的跑團點數"""
        user = db_user.get([ctx.author.id])[0]
        response = "你目前的點數為：{}".format(user.point)
        await ctx.send(response)

    @commands.command()
    async def donate(self, ctx, *args):
        """贈與點數給其他人

        範例：
        give @DolaTRPG 10
        give @DolaTRPG 10 轉讓理由"""
        user = db_user.get([ctx.author.id])[0]
        target_parsed = re.findall('^<@!?(\d+)>$', args[0])
        if not target_parsed:
            await ctx.send("目標不存在，請在伺服器內執行此指令")
            return
        target_discord_user = self.bot.get_user(int(target_parsed[0]))
        target_user = db_user.get([target_discord_user.id])[0]

        donate_point = int(args[1])
        if user.point < donate_point:
            # not enough points
            await ctx.send("你持有的點數({})不夠贈與({})".format(user.point, donate_point))
            return

        # points transition
        db_user.update(user.id, point=user.point - donate_point)
        db_user.update(target_user.id, point=target_user.point + donate_point)

        # notify users
        await ctx.author.send("已轉讓 {} 點給 {}，你的剩餘點數為 {}".format(donate_point, target_discord_user.name, user.point - donate_point))
        await target_discord_user.send("{} 轉讓 {} 點給你，你的現有點數為 {}".format(ctx.author.name, donate_point, target_user.point + donate_point))
        comment = " ".join(args[2:])
        if comment:
            await target_discord_user.send("轉讓理由：{}".format(comment))

    async def ban_abandoned_users(self):
        """remove abandoned users from database and send announcement message
        """
        abandoned_users = db_user.get_inactive(10 * 24 * 3600)  # user inactive for 10 days will be listed as abandoned
        for user in abandoned_users:
            db_user.remove(user.id)
            discord_user = self.bot.get_user(user.id)
            if not discord_user:
                # user already left server
                continue
            await self.bot.get_guild(self._server_id).ban(discord_user, reason="inactive detected at {}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
