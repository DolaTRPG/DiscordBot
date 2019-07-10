from datetime import datetime, timedelta
import random
import re
import time

import configurations
import googlesheet

import db_user
import discord
from discord.ext import commands
import util


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
        db_user.add(id=member.id, name=member.name)

    @commands.Cog.listener()
    async def on_message(self, message):
        """user takes action in discord server
        Args:
            (Discord.User) discord user class
        """
        discord_user = message.author
        user = db_user.get(discord_user.id)
        if not user:
            # add user if not exist
            db_user.add(id=discord_user.id, name=discord_user.name)
            return
        if user.activity_at < int(time.time()) - (12 * 3600):
            # user can get points for every 12 hours
            db_user.update(user.id, activity_at=time.time(), point=user.point + 1)
            await self.ban_abandoned_users()

    @commands.command()
    @commands.is_owner()
    async def edit(self, ctx, *args):
        """(管理者功能)修改使用者資料

        範例：
        edit @DolaTRPG point 10
        """
        target_parsed = re.findall('^<@!?(\d+)>$', args[0])
        if not target_parsed:
            await ctx.send("目標不存在，請在伺服器內執行此指令")
            return
        target_discord_user = self.bot.get_user(int(target_parsed[0]))
        update_item = {args[1]: int(args[2])}
        db_user.update(target_discord_user.id, **update_item)

    @commands.command(aliases=['points'])
    async def point(self, ctx):
        """查詢自己的跑團點數"""
        user = db_user.get(ctx.author.id)
        response = "你目前的點數為：{}".format(user.point)
        await ctx.send(response)

    @commands.command()
    async def donate(self, ctx, *args):
        """轉讓點數給其他人

        範例：
        give @DolaTRPG 10
        give @DolaTRPG 10 轉讓理由"""
        user = db_user.get(ctx.author.id)
        target_parsed = re.findall('^<@!?(\d+)>$', args[0])
        if not target_parsed:
            await ctx.send("目標不存在，請在伺服器內執行此指令")
            return
        target_discord_user = self.bot.get_user(int(target_parsed[0]))
        target_user = db_user.get(target_discord_user.id)

        donate_point = int(args[1])
        if user.point < donate_point:
            # not enough points
            await ctx.send("你持有的點數({})不夠轉讓({})".format(user.point, donate_point))
            return

        # points transition
        db_user.update(user.id, point=user.point - donate_point)
        db_user.update(target_user.id, point=target_user.point + donate_point)

        # notify users
        await ctx.author.send("已轉讓 {} 點給 {}，你的剩餘點數為 {}".format(donate_point, target_discord_user.mention, user.point - donate_point))
        await target_discord_user.send("{} 轉讓 {} 點給你，你的現有點數為 {}".format(ctx.author.mention, donate_point, target_user.point + donate_point))
        comment = " ".join(args[2:])
        if comment:
            await target_discord_user.send("轉讓理由：{}".format(comment))
        await util.log(self.bot, "轉讓點數：{}->{}, 點數：{}".format(ctx.author.mention, target_discord_user.mention, donate_point))

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
            reason = "inactive detected at {}".format(time.strftime('%Y-%m-%d %H:%M:%S'))
            await util.log(self.bot, reason)
            await self.bot.get_guild(self._server_id).ban(discord_user, reason=reason)
