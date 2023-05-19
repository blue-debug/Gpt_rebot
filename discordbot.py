import os
import json
import discord

with open("config.json", "r") as f: config = json.load(f)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('顶级')

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(config['bot_key'])