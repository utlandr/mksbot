import asyncio
import discord
import yaml
import random as r
from discord.ext import commands
from cogs.amusement_fun import *

'''Amusement class cog addon to mksbot main. Primarily contains random/non-admin type commands'''
class Amusement:
    def __init__(self, bot):
        self.bot = bot
        self.config = yaml.safe_load(open("config.yml"))
        self.client = discord.Client()

    #   Random twitch copy-paste from a local .txt list
    @commands.command(pass_context=True)
    async def donger(self, ctx):
        await ctx.send(get_random_donger())

    #   Configurable Russian Roulette style to kick users from a voice channel
    @commands.command(pass_context=True)
    async def roulette(self, ctx, to_kill=1, chambers=6):
        '''Play a game of Russian Roulette to kick members out of a discord voice channel'''
        
        try:
            channel = ctx.message.author.voice.channel
            guild = ctx.guild
            members = channel.members
            n_mem = len(members)
            
            if to_kill > n_mem:
                to_kill = n_mem
            
            elif to_kill == 0:
                to_kill = 1 
                    
        except:
            response = '{}: !roulette requires you to be in a voice channel'.format(ctx.message.author.mention)
            await ctx.send(response)
            return
        
        #   Load the weapon (randomly choose position to place bullets)
        if n_mem > 1:
            graveyard_vc = discord.utils.get(guild.voice_channels, category = channel.category, name = "R.I.P.")
            
            if not graveyard_vc:
                await guild.create_voice_channel(name = "R.I.P.", category = channel.category)
                graveyard_vc = discord.utils.get(guild.voice_channels, category = channel.category, name = "R.I.P.")

            
            if not chambers or chambers < to_kill:
                chambers = n_mem

            await ctx.send("MksBot loads {} rounds into his {} barrelled weapon".format(to_kill, chambers))

            death_chambers = r.sample(range(0,chambers), to_kill)
            shot = 0
            count = 0
            r.shuffle(members)
            
            while shot < to_kill:
                for member in members:
                    response, kill_check = russian_roulette(member.name, death_chambers, chambers, count)
                    await ctx.send(response)
                    await asyncio.sleep(0.7)
                    count += 1

                    if kill_check:
                        shot += 1
                        members.remove(member)
                        await member.move_to(graveyard_vc, reason = "Shot behind the barn by MksBot")
                        break

        else:
            response =  '{}: Unless you want to shoot yourself, !roulette requires at least 1 other person to be in your voice channel.'.format(ctx.message.author.mention)
            await ctx.send(response)
    
    #   This routine performs checks every time a user's voice state changes (such as switching voice channels)
    async def on_voice_state_update(self, member, before, after):
        b_channel = before.channel
        
        #   Remove temporary voice channel "R.I.P."
        if b_channel is not None:

            if b_channel.name == "R.I.P.":
                if not b_channel.members:
                    await b_channel.delete(reason="Everyone is revived")
        
        else:
            pass

def setup(bot):
    bot.add_cog(Amusement(bot))