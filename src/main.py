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
    if not message.channel.is_private:
        Users.increase_value(message.author, "exp", len(message.content))
        Users.check_level_up(message.author)

    # response with user information
    if message.channel.is_private:
        # avoid additional actions if user is already busy 
        if message.author in busy_users:
            return

        busy_users.append(message.author)

        if message.content == "點數":
            user_info = Users.get(message.author)
            response = "你目前的點數為：{}".format(user_info["points"])
            await client.send_message(message.channel, response)

        elif message.content == "創團":
            await Games.discord_create(client, message)

        elif message.content == "開團":
            await Games.discord_start(client, message)

        elif message.content == "報名":
            await Games.discord_join(client, message)

        else:
            response = "請輸入對應的指令：\n"
            response += "`點數`：查看你的點數\n"
            response += "`創團`：登記團務，募集玩家\n"
            response += "`開團`：收取點數，開始跑團\n"
            response += "`報名`：參加募集中的團\n"
            await client.send_message(message.channel, response)

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
