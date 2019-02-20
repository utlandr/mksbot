#   DISCLAIMER - Most of this cog is an adaptation of the 'basic-voice'
#   cog provided in Rapptz discord.py repository (under the examples subdirectory)

import discord
from discord.ext import commands

from cogs.voice.voice_fun import bot_audible_update
from cogs.voice.voice_fun import play_queue
from cogs.voice.voice_fun import queue
from cogs.voice.voice_fun import YTDLSource


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.def_volume = 0.1
        self.cur_volume = self.def_volume
        self.queues = {}
        self.players = {}

    #   Summon to voice channel
    @commands.command()
    async def summon(self, ctx, *arg):
        """Joins a voice channel

        :param ctx: command invocation message context
        :param arg:
        :return: None
        """

        #   Connect to a supplied voice channel
        if len(arg) != 0:
            channel = discord.utils.get(ctx.guild.voice_channels, name=arg[0])

            if channel is not None:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(channel)
                    await bot_audible_update(ctx, "Entering")
                    return

                await channel.connect()

        #   No input implies connect to users current voice channel
        else:
            channel = ctx.author.voice.channel
            if ctx.voice_client:
                await ctx.voice_client.move_to(channel)
            else:
                await ctx.author.voice.channel.connect()

            await bot_audible_update(ctx, "Entering")

    #   Leave the discord channel (also stops audio)
    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice

        :param ctx: command invocation message context
        :return: None
        """

        await bot_audible_update(ctx, "Leaving")
        await ctx.voice_client.disconnect()

    #   Play audio locally stored
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem

        :param ctx: command invocation message context
        :param query: YouTube search query
        :return: None
        """
        async with ctx.typing():
            player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
            player.title = query.split("/")[-1]

        guild_id = ctx.message.guild.id
        if guild_id in self.queues and ctx.voice_client.is_playing():
            await queue(self, ctx, player)

        else:
            self.queues[guild_id] = [player]
            response = "Starting a new queue"
            await ctx.send(response)
            play_queue(self, ctx)

    #   Download first from YT and play
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)

        :param ctx: command invocation message context
        :param url: YouTube video url
        :return: None
        """

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)

        guild_id = ctx.message.guild.id
        if guild_id in self.queues and ctx.voice_client.is_playing():
            await queue(self, ctx, player)

        else:
            self.queues[guild_id] = [player]
            response = "Starting a new queue"
            await ctx.send(response)
            play_queue(self, ctx)

    #   Stream (no local storage) Youtube audio
    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)

        :param ctx: command invocation message context
        :param url: YouTube video URL
        :return:
        """

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

        guild_id = ctx.message.guild.id
        if guild_id in self.queues and ctx.voice_client.is_playing():
            await queue(self, ctx, player)

        else:
            self.queues[guild_id] = [player]
            response = "Starting a new queue"
            await ctx.send(response)
            play_queue(self, ctx)

    #   Alter volume of audio
    @commands.command()
    async def volume(self, ctx, *volume: int):
        """Changes the player's volume

        :param ctx: command invocation message context
        :param volume: volume to set the player to
        :return: message reply on successful volume update
        """

        try:
            bot_volume = ctx.voice_client.source.volume

        except AttributeError:
            return await ctx.send("Audio not initialized\nDefault audio volume is {}%".format(self.def_volume * 100))

        if volume:
            if volume[0] in range(1, 101) and volume[0] != int(bot_volume * 100):
                if ctx.voice_client is None:
                    return await ctx.send("You are not connected to a voice channel.")

                ctx.voice_client.source.volume = volume[0]/100
                self.cur_volume = volume[0]/100
                return await ctx.send("Changed volume to {}%".format(int(volume[0])))

        return await ctx.send("Current volume is {}%".format(int(bot_volume * 100)))

    #   Pause current audio stream
    @commands.command()
    async def pause(self, ctx):
        """Pauses current playback

        :param ctx: command invocation message context
        :return: None
        """

        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
    
    #   Resume current audio stream
    @commands.command()
    async def resume(self, ctx):
        """Resumes current playback if paused

        :param ctx: command invocation message context
        :return: None
        """
        
        ctx.voice_client.resume()

    #   Skip current song and play the next one
    @commands.command()
    async def skip(self, ctx):
        """Skips current player and player the next player in the queue

        :param ctx:
        :return:
        """
        player_title = ctx.voice_client.source.title
        await ctx.send("Skipping:\t{}".format(player_title))
        ctx.voice_client.stop()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        """Checks made on selection command before invocation

        :param ctx: command invocation message context
        :return:
        """
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                await bot_audible_update(ctx, "Entering")
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

    #   Checks playback commands for proper invocation
    @pause.before_invoke
    @resume.before_invoke
    @skip.before_invoke
    @leave.before_invoke
    async def ensure_user_presence(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")


def setup(bot):
    bot.add_cog(Music(bot))
