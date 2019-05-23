import asyncio
import discord
import os
import json

import users
import games

token = os.environ['discord_token']
google_spreadsheet_key = os.environ['google_spreadsheet_key']
game_server_id = int(os.environ['discord_server_id'])
game_channel_id = int(os.environ['discord_game_channel_id'])
newcomer_role_name = os.environ['discord_newcomer_role_name']
client = discord.Client()

Users = users.Users(google_spreadsheet_key)
busy_users = []


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_raw_reaction_add(event):
    if event.channel_id == game_channel_id:
        message = await client.get_channel(event.channel_id).fetch_message(event.message_id)
        await games.start(client, message, Users)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # increase exp for public chat
    if not is_channel_type(message.channel, "DMChannel"):
        Users.increase_value(message.author, "exp", len(message.content))
        Users.check_level_up(message.author)

    # reaction in direct message
    if is_channel_type(message.channel, "DMChannel"):
        # avoid additional actions if user is already busy
        if message.author in busy_users:
            return

        busy_users.append(message.author)

        if message.content == "點數":
            user_info = Users.get(message.author)
            response = "你目前的點數為：{}".format(user_info["points"])
            await message.channel.send(response)
            print("{} 查詢點數：{}".format(message.author.name, user_info["points"]))

        elif message.content == "開團":
            await games.create(client, message, game_channel_id)

        # save current progress into storage
        elif message.content.startswith('!save'):
            Users.write()
            await message.channel.send("更新完成")

        else:
            response = "請輸入對應的指令：\n"
            response += "`點數`：查看你的點數\n"
            response += "`開團`：登記團務，募集玩家\n"
            await message.channel.send(response)

        busy_users.remove(message.author)


@client.event
async def on_message_delete(message):
    # ignore action if happens in direct message
    if is_channel_type(message.channel, "DMChannel"):
        return

    # decrease user points by 1 when delete message
    Users.increase_value(message.author, "points", -1)
    Users.write()


@client.event
async def on_member_join(member):
    server = client.get_guild(game_server_id)
    role = discord.utils.get(server.roles, name=newcomer_role_name)
    await member.add_roles(role)


def is_channel_type(channel, class_name):
    """check if channel is private
    Args:
        - (discord channel) channel class
        - (str) class_name - discord class name (e.g. DMChannel)
    """
    if channel.__class__.__name__ == class_name:
        return True
    return False


client.run(token)
