import asyncio
import discord
import os
import json

import users
import log_horizon

token = os.environ['discord_token']
google_spreadsheet_key = os.environ['google_spreadsheet_key']
client = discord.Client()

Users = users.Users(google_spreadsheet_key)


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

    # temp test for log horizon
    if message.content.startswith("lh"):
        player_id = message.content.split(' ')[-1]
        response = log_horizon.get_skill_macros(player_id)
        await client.send_message(message.channel, response)
        return

    # increase exp for public chat
    if not message.channel.is_private:
        Users.increase_value(message.author, "exp", len(message.content))
        Users.check_level_up(message.author)

    # response with user information
    if message.channel.is_private:
        if message.content == "點數":
            user_info = Users.get(message.author)
            response = "你目前的點數為：{}".format(user_info["points"])
            await client.send_message(message.channel, response)

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
