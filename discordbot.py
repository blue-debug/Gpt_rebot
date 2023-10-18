import os
import json
import discord
from discord.ext import commands
import logging
import openai
import requests
import io

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

with open("config.json", "r") as f: 
    config = json.load(f)

openai.api_key = os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents = intents)

@bot.event
async def on_ready():
    print('Logged on as', bot.user)

@bot.event
async def on_message(message):
    # don't respond to ourselves
    if message.author == bot.user:
        return

    if message.content == 'ping':
        await message.channel.send('pong')

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def start(ctx):
    await ctx.send('Started!')

@bot.command()
async def image(ctx, text: str):
    requirment = text
    print("Image: %s", requirment)
    response = openai.Image.create(
        prompt = requirment,
        n = 1,
        size = "256x256" # 256x256 512x512 1024x1024
    )
    image_url = response['data'][0]['url']
    print(image_url)
    # await ctx.send(image_url)

    response = requests.get(image_url)
    image_data = io.BytesIO(response.content)
    await ctx.send(file = discord.File(fp = image_data, filename = 'image.png'))
    image_data = None
    
@bot.command()
async def chat(ctx, text: str):
    text_list = []
    text_list.append({"role": "user", "content": text})
    response = openai.ChatCompletion.create(model = "gpt-3.5-turbo", messages = text_list)
    print(response.choices[0]['message']['content'])
    await ctx.send(response.choices[0]['message']['content'])


bot.run(config['bot_key'], log_handler = handler, log_level = logging.DEBUG)