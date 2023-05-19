import os
import json
import discord

import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

with open("config.json", "r") as f: config = json.load(f)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
    
    async def on_message(self, message):
        # don't respond to ourselves
        # logging.debug(message)
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

        if message.content == '顶级':
            await message.channel.send('顶级')

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents = intents)
client.run(config['bot_key'], log_handler = handler, log_level = logging.DEBUG)