import asyncio
import discord
from discord.ext import commands
import logging
import random
import sys, traceback
import yaml

from base_functions import *
from cogs.amusement_fun import get_random_donger

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

#   Import config data
config = yaml.safe_load(open("./config.yml"))


bot = commands.Bot(command_prefix='!', description = config['bot']['description'])
client = discord.Client()

#   Import cogs/extensions
cogs = ['cogs.reddit',
        'cogs.amusement',
        'cogs.voice'
        ]
        
if __name__ == '__main__':
    for extension in cogs:
        try:
            bot.load_extension(extension)

        except Exception as e:
            print('Failed to load extension {}.'.format(extension), file=sys.stderr)
            traceback.print_exc()

#   Successful connection to server
@bot.event
async def on_ready(pass_context=True):
    print('\n\nLogged in as\nUsername:  %s\nID  %s\n\n' % (bot.user.name, bot.user.id))


bot.remove_command('help')

#   Basic commands (usually single response)
@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="MksBot", description="My commands are:", color=0xeee657)
    embed.add_field(name="!info", value="Bot info", inline=False)
    embed.add_field(name="!help", value="Gives this message", inline=False)
    embed.add_field(name="!copypasta", value=config['copypasta']['description'], inline=False)
    embed.add_field(name="!donger", value=get_random_donger(), inline=False)
    embed.add_field(name="!roulette <no. to kill> <no. of chambers>", value=config['roulette']['description'], inline = False)
    embed.add_field(name="!volume <1-10>", value=config['volume']['description'], inline=False)
    embed.add_field(name="!play <filename>", value=config['play']['description'], inline=False)
    embed.add_field(name="!stream <url or search term>", value=config['stream']['description'], inline=False)
    embed.add_field(name="!yt <url or search term>", value=config['youtube']['description'], inline=False)
    embed.add_field(name="!stop", value=config['stop']['description'], inline=False)
    embed.add_field(name="!summon <voice channel>", value=config['summon']['description'], inline=False)
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def info(ctx):
    embed = discord.Embed(title=config['bot']['title'], description=config['bot']['description'], color=0xeee657)
    embed.add_field(inline = False, name="Where humans can complain", value = config['bot']['email'])
    embed.add_field(inline = False, name = "Where humans can see my beautiful code", value = config['bot']['source_code'])
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def user(ctx, *, member : discord.Member):
    await ctx.send(embed = user_info_embed(member))

@user.error
async def user_error(ctx, error):
    if isinstance(error,  commands.BadArgument):
        print(error)

#   Logging options
logger = logging.getLogger('discord')

if config['bot']['log_level'] == 'debug':
    logger.setLevel(logging.DEBUG)

else:
    logger.setLevel(logging.WARNING)

handler = logging.FileHandler(filename='{}/mksbot.log'.format(config['bot']['log_path']), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot.run(config["bot"]["token"])
client.run(config["bot"]["token"])
