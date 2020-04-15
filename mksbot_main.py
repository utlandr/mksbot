import logging
import sys
import traceback
import yaml

from cogs.reddit.reddit import Reddit
from cogs.amusement.amusement import Amusement
from cogs.voice.voice import Music
from discord.ext import commands


from base_functions import *

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

#   Import config data and extensions (cogs)
config = yaml.safe_load(open("./config.yml"))

bot = commands.Bot(command_prefix='!', description=config['bot']['description'])
client = discord.Client()

cogs = [Reddit(bot),
        Amusement(bot),
        Music(bot)]
        
if __name__ == '__main__':
    for extension in cogs:
        try:
            bot.add_cog(extension)

        except Exception as e:
            print('Failed to load extension {}.'.format(extension), file=sys.stderr)
            traceback.print_exc()


#   Base bot commands
bot.remove_command('help')


@bot.event
async def on_ready():
    """Successful connection to server
    """
    print('\n\nLogged in as\nUsername:  %s\nID  %s\n\n' % (bot.user.name, bot.user.id))


@bot.command(pass_context=True)
async def info(ctx):
    """Display basic information/help/details on the bot
    """
    embed = discord.Embed(title=config['bot']['title'],
                          description=config['bot']['description'],
                          color=0xeee657)

    embed.add_field(inline=False,
                    name="Where humans can complain",
                    value=config['bot']['email'])

    embed.add_field(inline=False,
                    name="Where humans can see my beautiful code",
                    value=config['bot']['source_code'])

    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def user(ctx, *, member: discord.Member):
    """Get user information
    """
    await ctx.send(embed=user_info_embed(member))


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def rm(ctx, *number):
    """Remove messages one-by-one in the invoked text channel

    :param ctx: command invocation message context
    :param number: the number of posts to remove
    :return: None
    """

    limit = 1
    if number:
        try:
            n = int(number[0])

            if n > 0:
                limit = n

        except ValueError as e:
            if number[0] == "purge":
                limit = None

    await ctx.channel.purge(limit=limit, bulk=False)


@user.error
async def user_error(error):
    """Handle user method error
    """
    if isinstance(error,  commands.BadArgument):
        print(error)


#   Basic commands (usually single response)
@bot.command(pass_context=True)
async def help(ctx, *args):
    """Display command information and invocation syntax

    :param ctx: command invocation message context
    :param args: If given, the specific command for further detail
    :return: None
    """
    if not args:
        embed = discord.Embed(title=" ",
                              description=" ",
                              color=0xeee657)

        embed.set_author(name="MksBot Help",
                         url="https://github.com/utlandr/mksbot",
                         icon_url="http://www.clipartbest.com/cliparts/aie/65d/aie65d4bT.png")

        for category in config["help"]:

            embed.add_field(name="\u200b", value=category, inline=False)

            for command_name in config["help"][category]:
                comm = config["help"][category][command_name]
                embed.add_field(name=comm["invocation"], value="\u200b", inline=True)

        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Use !help <command> for more information on a specific command", value="\u200b", inline=False)
        await ctx.send(embed=embed)

    else:
        c_group = []
        just_c = []
        command = args[0].replace("!", "")
        [[c_group.append(group) for c in config["help"][group]] for group in config["help"]]
        [[just_c.append(c) for c in config["help"][group]] for group in config["help"]]
        if command in just_c:
            ind = just_c.index(command)
            details = config["help"][c_group[ind]][command]
            embed = discord.Embed(title=" ",
                                  description=" ",
                                  color=0xeee657)

            embed.set_author(name="MksBot Help: !" + command,
                             url="https://github.com/utlandr/mksbot",
                             icon_url="http://www.clipartbest.com/cliparts/aie/65d/aie65d4bT.png")

            embed.add_field(name="Description", value=details["description"], inline=False)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Invocation", value=details["example"], inline=False)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Options", value=details["options"], inline=False)

            await ctx.send(embed=embed)


#   Logging options and formatting
logger = logging.getLogger('discord')
if config['bot']['log_level'] == 'debug':
    logger.setLevel(logging.DEBUG)

elif config['bot']['log_level'] == 'info':
    logger.setLevel(logging.INFO)

elif config['bot']['log_level'] == 'warning':
    logger.setLevel(logging.WARNING)

else:
    logger.setLevel(logging.ERROR)

handler = logging.FileHandler(filename='{}/mksbot.log'.format(config['bot']['log_path']), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#   Initiate discord bot and client instance
bot.run(config["bot"]["token"])
client.run(config["bot"]["token"])
