from datetime import datetime, timedelta
import random
import time

import googlesheet


class Users:
    def __init__(self, google_spreadsheet_key, client, server_id):
        self._client = client
        self._server_id = server_id
        self._columns = ["id", "name", "points", "gm", "points_earned", "player", "points_used", "last_activity"]
        self._storage = googlesheet.Storage(google_spreadsheet_key, "users", self._columns)
        self.read()

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

    def write(self):
        """output users into DB
        Return:
            (str) output worksheet name (e.g. users_20190101_123456)
        """
        worksheet_name = self._storage.write_data(self._users)
        return worksheet_name

    def add(self, discord_user):
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
        ids = [u['id'] for u in self._users]
        if discord_user.id not in ids:
            self.add(discord_user)

        for user in self._users:
            if user['id'] == int(discord_user.id):
                return user
        return None

    async def active(self, discord_user):
        """user takes action in discord server
        Args:
            (Discord.User) discord user class
        """
        user = self.get(discord_user)
        if not user:
            self.add(discord_user)
            return
        last_activity = datetime.strptime(user['last_activity'], '%Y-%m-%d %H:%M:%S')
        if last_activity < datetime.now() - timedelta(hours=12):
            # user can get points for every 12 hours
            user['last_activity'] = time.strftime('%Y-%m-%d %H:%M:%S')
            user['points'] += 1
            await self.write()

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
            discord_user = self._client.get_user(user_id)
            await self._client.get_guild(self._server_id).ban(discord_user, reason="idle detected at {}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        self._users = [x for x in self._users if x['id'] not in abandoned_users]
