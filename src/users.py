import random
import time

import googlesheet


class Users:
    def __init__(self, google_spreadsheet_key):
        self._columns = ["user_id", "points", "gm", "player", "points_used", "points_earned", "exp"]
        self._storage = googlesheet.Storage(google_spreadsheet_key)
        self.read()
        print(self._users)

    def read(self):
        """load users from DB
        Return:
            (None)
        """
        self._users = self._storage.read_users()

    def write(self):
        """output users into DB
        Return:
            (str) output worksheet name (e.g. users_20190101_123456)
        """
        worksheet_name = self._storage.write_users(self._users)
        return worksheet_name

    def add(self, discord_user):
        """add new user
        Args:
            (Discord.User) discord user class
        Return:
            (dict) user information
                {
                    "user_id": 0,
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
        user["user_id"] = int(discord_user.id)
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
                    "user_id": 0,
                    "points": 10,
                    "gm": 10,
                    "player": 3,
                    "points_used": 100,
                    "points_earned": 100,
                    "exp": 0
                }
        """
        for user in self._users:
            if user['user_id'] == int(discord_user.id):
                return user
        return None

    def check_level_up(self, discord_user):
        """check if exp is enough to level up
        Args:
            (Discord.User) discord user class
        Return:
            (True) user level up
            (False) user did not level up
            (None) user not exist
        """
        user = self.get(discord_user)
        if not user:
            return None
        current_level = user["points"] + 1
        upgrade_exp = random.randint(0, current_level * 100)
        if upgrade_exp < user["exp"]:
            self._level_up(discord_user)
            self.write()
            return True
        return False

    def _level_up(self, discord_user):
        """level up for user
        Args:
            (Discord.User) discord user class
        Return:
            (None)
        """
        for user in self._users:
            if user["user_id"] == int(discord_user.id):
                user["points"] += 1
                user["exp"] = 0
                return

    def increase_value(self, discord_user, key, value):
        """increase value for user
        Args:
            (Discord.User) discord user class
            (str) key -- key to update
            (int) value -- increase value
        Return:
            (dict) user information
                {
                    "user_id": 0,
                    "points": 10,
                    "gm": 10,
                    "player": 3,
                    "points_used": 100,
                    "points_earned": 100,
                    "exp": 0
                }
        """
        for user in self._users:
            if int(user['user_id']) == int(discord_user.id):
                user[key] += value
                user['last_activity'] = time.strftime('%Y-%m-%d %H:%M:%S')
                return user
        else:
            user = self.add(discord_user)
            return user
