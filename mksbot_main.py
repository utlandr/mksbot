import logging
import discord
import random
from discord.ext import commands

try:
with open("token.txt", "r") as token_file:
    token = token_file.readline()
except:
    print("Error: No token file found. Exiting.")


bot = commands.Bot(command_prefix='!')

#   Successful connection to server
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)

#   Setup logging
logging.basicConfig(level=logging.DEBUG)

bot.run(token)