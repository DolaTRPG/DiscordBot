import asyncio
import discord
import os
import json

import users
import games

token = os.environ['discord_token']
google_spreadsheet_key = os.environ['google_spreadsheet_key']
client = discord.Client()

Users = users.Users(google_spreadsheet_key)
Games = games.Games(google_spreadsheet_key)
busy_users = []


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(int(client.user.id))
    print('------')


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # increase exp for public chat
    if not message.channel.__class__.__name__ == "DMChannel":
        Users.increase_value(message.author, "exp", len(message.content))
        Users.check_level_up(message.author)

    # response with user information
    if message.channel.__class__.__name__ == "DMChannel":
        # avoid additional actions if user is already busy
        if message.author in busy_users:
            return

        busy_users.append(message.author)

        if message.content == "點數":
            user_info = Users.get(message.author)
            response = "你目前的點數為：{}".format(user_info["points"])
            await message.channel.send(response)

        elif message.content == "開團":
            await games.create(client, message)

        else:
            response = "請輸入對應的指令：\n"
            response += "`點數`：查看你的點數\n"
            response += "`開團`：登記團務，募集玩家\n"
            await message.channel.send(response)

        busy_users.remove(message.author)

    # save current progress into storage
    if message.content.startswith('!save'):
        Users.write()


@client.event
async def on_message_delete(message):
    # ignore action if happens in private channel
    if message.channel.is_private:
        return

    # decrease user points by 1 when delete message
    Users.increase_value(message.author, "points", -1)
    Users.write()


client.run(token)
