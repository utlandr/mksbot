import discord
from discord.ext import commands

from cogs.voice.voice_fun import bot_audible_update
from cogs.voice.voice_fun import create_playing_embed
from cogs.voice.voice_fun import create_queue_embed
from cogs.voice.voice_fun import droid_speak_translate
from cogs.voice.voice_fun import format_duration
from cogs.voice.voice_fun import play_queue
from cogs.voice.voice_fun import add_queue
from cogs.voice.voice_fun import YTDLSource


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.def_volume = 0.05
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
                    return

                await channel.connect()
                await bot_audible_update(ctx, "Entering")

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
        guild_id = ctx.message.guild.id
        if ctx.voice_client:
            del self.queues[guild_id][:]

        await ctx.voice_client.disconnect()

    #   Stream (no local storage) Youtube audio
    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)

        :param ctx: command invocation message context
        :param url: YouTube video URL
        :return:
        """
        async with ctx.typing():
            source = await YTDLSource.get_info(url)
            if source.videos:
                await add_queue(self, ctx, source)
            else:
                await ctx.send("Media not found.")

        if ctx.voice_client.is_paused() or ctx.voice_client.is_playing():
            pass
        else:
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
            bot_volume = int(ctx.voice_client.source.volume * 100)

        except AttributeError:
            perc_vol = self.def_volume * 100
            msg = "Audio not initialized\nDefault audio volume is {}%".format(perc_vol)
            return await ctx.send(msg)

        if volume:
            if volume[0] in range(1, 101) and volume[0] != bot_volume:
                if ctx.voice_client is None:
                    return await ctx.send("You are not connected to a voice channel.")

                ctx.voice_client.source.volume = volume[0] / 100
                self.cur_volume = volume[0] / 100
                return await ctx.send("Changed volume to {}%".format(int(volume[0])))

        return await ctx.send("Current volume is {}%".format(bot_volume))

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
    async def skip(self, ctx, *queue_id):
        """Skips current player and plays the next player in the queue

        :param ctx: command invocation message context
        :param queue_id: 1-based queue index to remove player
        :return:
        """
        guild_id = ctx.message.guild.id
        if queue_id:
            if queue_id[0] == "all":
                del self.queues[guild_id][:]
                ctx.voice_client.stop()
                await ctx.send("Queue has been emptied.")
            elif int(queue_id[0]) and int(queue_id[0]) <= len(self.queues[guild_id]):
                removed = self.queues[guild_id].pop(int(queue_id[0]) - 1).title
                await ctx.send("Removed:\t{}".format(removed))
        else:

            player_title = self.queues[guild_id][0].title
            await ctx.send("Skipping:\t{}".format(player_title))
            ctx.voice_client.stop()

    #   Display information about current audio being played
    @commands.command()
    async def player(self, ctx):
        """Display information about current audio being played

        :param ctx: command invocation message context
        :return:
        """
        queue = self.queues.get(ctx.message.guild.id)
        if ctx.voice_client:
            if queue:
                source = queue[0]
                status = "Paused" if ctx.voice_client.is_paused() else "Playing"
                embed_playing = create_playing_embed(source, status)
                await ctx.send(embed=embed_playing)

    #   View the queue of the existing playlist
    @commands.command()
    async def queue(self, ctx, first=5):
        """

        :param ctx: command invocation message context
        :param first: the number of audio sources to display in the embed
        :return:
        """
        guild_id = ctx.message.guild.id
        queue_cp = self.queues[guild_id].copy()

        if guild_id in self.queues:
            embed_queue = create_queue_embed(title="MksBot Player Queue")
            queue_string = ""
            count = 0

            for aud_source in queue_cp[:first]:
                playlist_id = count if count else "Playing"

                if aud_source.is_live:
                    duration = "LIVE"

                else:
                    duration = format_duration(aud_source.duration)

                queue_string += "{0}. {1} | [{2}](https://youtube.com/watch?v={3})\n\n".format(playlist_id,
                                                                                               duration,
                                                                                               aud_source.title,
                                                                                               aud_source.id)
                count += 1

            embed_queue.add_field(name="Total in Queue",
                                  value=len(queue_cp))
            embed_queue.add_field(name="\u200b",
                                  value="\u200b",
                                  inline=False)
            embed_queue.add_field(name=f"Queue (Displaying first {first})",
                                  value=queue_string,
                                  inline=False)
            await ctx.send(embed=embed_queue)

    @commands.command()
    async def speak(self, ctx, *phrase: str):
        """Have the bot translate a phrase into Droidspeak (activate Star Wars Nerd Mode)

        :param ctx: command invocation message context
        :return: None
        """
        if not ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await droid_speak_translate(ctx, phrase)

    @stream.before_invoke
    @speak.before_invoke
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
