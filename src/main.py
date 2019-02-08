import asyncio
import discord
import os
import json

import users

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

    # increase exp for public chat
    if not message.channel.is_private:
        Users.increase_value(message.author, "exp", len(message.content))
        Users.check_level_up(message.author)

    # response with user information
    if message.channel.is_private:
        user_info = Users.get(message.author)
        await client.send_message(message.channel, json.dumps(user_info))

    # save current progress into storage
    if message.content.startswith('!save'):
        Users.write()

client.run(token)
