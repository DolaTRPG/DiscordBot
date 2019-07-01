from datetime import datetime, timedelta
import random
import re
import time

import configurations
import googlesheet

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
        await self.add(member)

    @commands.Cog.listener()
    async def on_message(self, message):
        """user takes action in discord server
        Args:
            (Discord.User) discord user class
        """
        discord_user = message.author
        user = self.get(discord_user)
        if not user:
            await self.add(discord_user)
        else:
            last_activity = datetime.strptime(user['last_activity'], '%Y-%m-%d %H:%M:%S')
            if last_activity < datetime.now() - timedelta(hours=12):
                # user can get points for every 12 hours
                user['last_activity'] = time.strftime('%Y-%m-%d %H:%M:%S')
                user['points'] += 1
                await self.write()

    @commands.command(aliases=['points'])
    async def point(self, ctx):
        """查詢自己的跑團點數"""
        user = self.get(ctx.author)
        response = "你目前的點數為：{}".format(user["points"])
        await ctx.send(response)

    @commands.command()
    async def donate(self, ctx, *args):
        """贈與點數給其他人

        範例：
        give @DolaTRPG 10
        give @DolaTRPG 10 轉讓理由"""
        user = self.get(ctx.author)
        target_parsed = re.findall('^<@!?(\d+)>$', args[0])
        if not target_parsed:
            await ctx.send("目標不存在")
            return
        target_discord_user = self.bot.get_user(int(target_parsed[0]))
        target_user = self.get(target_discord_user)

        points = int(args[1])
        if user["points"] < points:
            # not enough points
            await ctx.send("你持有的點數({})不夠贈與({})".format(user['points'], points))
            return

        # points transition
        user['points'] -= points
        target_user['points'] += points

        # notify users
        await ctx.author.send("已轉讓 {} 點給 {}，你的剩餘點數為 {}".format(points, target_discord_user.name, user['points']))
        await target_discord_user.send("{} 轉讓 {} 點給你，你的現有點數為 {}".format(ctx.author.name, points, target_user['points']))
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

    def increase_value(self, discord_user, key, value):
        """increase value for user
        Args:
            (Discord.User) discord user class
            (str) key -- key to update
            (int) value -- increase value
        Return:
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
            if int(user['id']) == int(discord_user.id):
                user[key] += value
                if user[key] < 0:
                    user[key] = 0
                user['last_activity'] = time.strftime('%Y-%m-%d %H:%M:%S')
                return user
        else:
            user = self.add(discord_user)
            return user

    def penalty(self):
        """reduce points for idle players
        Return:
            - None
        """
        for user in self._users:
            user_activity = datetime.strptime(user['last_activity'], '%Y-%m-%d %H:%M:%S')
            if user_activity < datetime.now() - timedelta(days=1):
                if user['points'] > 0:
                    user['points'] -= 1
                    user['last_activity'] = time.strftime('%Y-%m-%d %H:%M:%S')

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
        abandoned_users = self.get_abandoned_user_ids()
        for user_id in abandoned_users:
            discord_user = self.bot.get_user(user_id)
            if not discord_user:
                # user already left server
                continue
            await self.bot.get_guild(self._server_id).ban(discord_user, reason="idle detected at {}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        self._users = [x for x in self._users if x['id'] not in abandoned_users]
