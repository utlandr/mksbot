import asyncio
import random as r
from typing import Any

import discord
import yaml
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context, command
from discord.member import Member

from mksbot.cogs.amusement.amusement_fun import get_random_donger, russian_roulette, target_spam


#   Amusement class cog addon to mksbot main. Primarily contains random/non-admin type commands
class Amusement(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = yaml.safe_load(open("config.yml"))
        self.client = discord.Client(intents=discord.Intents.all())

    @command(pass_context=True)
    async def donger(self, ctx: Context[Any]) -> None:
        """Call donger method and send to discord

        :param ctx: discord message context
        :return: None
        """

        await ctx.send(get_random_donger())

    @commands.command(pass_context=True)
    async def roulette(self, ctx: Context[Any], to_kill: int = 1, chambers: int = 6, mode: str = "kill") -> None:
        """Play a game of Russian Roulette to kick members out of a discord voice channel

        :param ctx: command invocation message context
        :param to_kill: number of members in the voice channel to remove
        :param chambers: number of 'trigger' events to remove players
        :param mode: mode game mode (kill or nerf)
        :return: None
        """

        #   If a user invokes !roulette and is not in a channel, an
        #   AttributeError occurs.
        author = ctx.message.author
        guild = ctx.guild
        assert guild is not None
        assert isinstance(author, Member)
        n_mem = 0
        if not author.voice:
            response = "{}: !roulette requires you to be in a voice channel".format(ctx.message.author.mention)
            await ctx.send(response)
            return
        channel = author.voice.channel
        if channel:
            members = channel.members
            n_mem = len(members)

            if to_kill > n_mem:
                to_kill = n_mem

            elif to_kill == 0:
                to_kill = 1

            #   Load the weapon (randomly choose position to place bullets)
            if n_mem > 1:
                #   Attempt to grab R.I.P. voice channel object, else create it.
                graveyard_vc = discord.utils.get(guild.voice_channels, category=channel.category, name="R.I.P.")

                if not graveyard_vc:
                    await guild.create_voice_channel(name="R.I.P.", category=channel.category)
                    graveyard_vc = discord.utils.get(guild.voice_channels, category=channel.category, name="R.I.P.")

                #   Set numbers of 'chambers'
                if not chambers or chambers < to_kill:
                    chambers = n_mem

                await ctx.send("MksBot loads {} rounds into the {} barrel revolver".format(to_kill, chambers))

                #   Randomly shuffle and designate members to 'kill'
                death_chambers = r.sample(range(0, chambers), to_kill)
                shot = 0
                count = 0
                r.shuffle(members)

                #   Iterate through all voice channel members and 'kill' randomly selected members
                while shot < to_kill:
                    for member in members:
                        response, kill_check = russian_roulette(member.name, death_chambers, count)
                        await ctx.send(response)
                        await asyncio.sleep(0.7)
                        count += 1

                        if kill_check:
                            if mode == "kill":
                                members.remove(member)
                                await member.move_to(graveyard_vc, reason="Shot behind the barn by MksBot")
                            shot += 1
                            break

            else:
                response = "{} Has a death wish. Denied.".format(ctx.message.author.mention)
                await ctx.send(response)

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def gather(self, ctx: Context[Any], *targets: str) -> None:
        """Spams a provided set of user names to get on the server

        :param ctx: command invocation message context
        :param targets: A list of targets

        :return: None
        """
        guild = ctx.guild
        if targets and guild:
            for target in targets:
                target_member = discord.utils.find(
                    lambda m: m.name == target or m.mention == target.replace("!", ""),
                    guild.members,
                )
                if target_member:
                    await ctx.send("Spamming {}".format(target))
                    await target_spam(target_member)

                else:
                    await ctx.send("Target '{}' not found".format(target))

        else:
            await ctx.send("No targets supplied")


#   discord.py uses this function to integrate the class+methods into the bot.
async def setup(bot: Bot) -> None:
    await bot.add_cog(Amusement(bot))
