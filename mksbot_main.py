import asyncio
import discord
from discord.ext import commands
import logging
import random
import yaml

from misc_functions import *
from reddit import *

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

#   Import config data
config = yaml.safe_load(open("./config.yml"))
bot = commands.Bot(command_prefix='!')

#   Successful connection to server
@bot.event
async def on_ready(pass_context=True):
    print('\n\nLogged in as\nUsername:  %s\nID  %s\n\n' % (bot.user.name, bot.user.id))

#   Commands
@bot.command(pass_context=True)
async def copypasta(ctx):
    title,content = hot_copypasta(5)
    pasta_response = discord.Embed(title = title, description = content, color = config["copypasta"]["response_colour"])
    await ctx.send(embed = pasta_response)

@bot.command(pass_context=True)
async def donger(ctx):
    await ctx.send(get_random_donger())

@bot.command(pass_context=True)
async def info(ctx):
    embed = discord.Embed(title=config['bot']['title'], description=config['bot']['description'], color=0xeee657)
    embed.add_field(inline = False, name="Where humans can complain", value = config['bot']['email'])
    embed.add_field(inline = False, name = "Where humans can see my beautiful code", value = config['bot']['source_code'])
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def user(ctx, member : discord.Member):
    await ctx.send(embed = user_info_embed(member))

bot.remove_command('help')

@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="MksBot", description="My commands are:", color=0xeee657)

    embed.add_field(name="!copypasta", value=config['copypasta']['description'], inline=False)
    embed.add_field(name="!donger", value=get_random_donger(), inline=False)
    embed.add_field(name="!user", value=config['user']['description'], inline=False)

    embed.add_field(name="!info", value="Bot info", inline=False)
    embed.add_field(name="!help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)


#   Setup logging
logging.basicConfig(level=logging.DEBUG)

bot.run(config["bot"]["token"])
