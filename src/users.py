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
        self._columns = ["id", "name", "points", "gm", "points_earned", "player", "points_used", "last_activity"]
        self._storage = googlesheet.Storage(google_spreadsheet_key, "users", self._columns)
        self.read()

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
        await self.write()

    def read(self):
        """load users from DB
        Return:
            (None)
        """
        data_rows = self._storage.read_data()
        self._users = []
        for row in data_rows:
            user = {}
            for key, value in zip(self._columns, row):
                try:
                    user[key] = int(value)
                except ValueError:
                    user[key] = value
            self._users.append(user)

    async def write(self):
        """output users into DB
        Return:
            (str) output worksheet name (e.g. users_20190101_123456)
        """
        await self.ban_abandoned_users()
        worksheet_name = self._storage.write_data(self._users)
        return worksheet_name

    async def add(self, discord_user):
        """add new user
        Args:
            (Discord.User) discord user class
        Return:
            (dict) user information
                {
                    "id": 0,
                    "name": "username",
                    "points": 10,
                    "gm": 10,
                    "player": 3,
                    "points_used": 100,
                    "points_earned": 100,
                    "exp": 0
                }
        """
        if discord_user.id == self.bot.user.id:
            # avoid adding bot into database
            return

        user = {}
        for key in self._columns:
            user[key] = 0
        user["id"] = int(discord_user.id)
        user["name"] = discord_user.name
        user["last_activity"] = time.strftime('%Y-%m-%d %H:%M:%S')
        self._users.append(user)
        await self.write()
        return user

    def get(self, discord_user):
        """get user information
        Args:
            (Discord.User) discord user class
        Return:
            (None) user not existed
            (dict) user information
                {
                    "id": 0,
                    "points": 10,
                    "gm": 10,
                    "player": 3,
                    "points_used": 100,
                    "points_earned": 100,
                    "exp": 0
                }
        """
        for user in self._users:
            if user['id'] == int(discord_user.id):
                return user
        return None

    def get_abandoned_user_ids(self):
        """users which does not appear anymore
        Return:
            - (list) user ids
        """
        abandoned_users = []
        for user in self._users:
            user_activity = datetime.strptime(user['last_activity'], '%Y-%m-%d %H:%M:%S')
            if user_activity < datetime.now() - timedelta(days=10):  # user inactive for 10 days will be listed as abandoned
                abandoned_users.append(user['id'])
        return abandoned_users

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
