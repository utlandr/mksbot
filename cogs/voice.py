#   DISCLAIMER - Most of this cog is an adaptation of the 'basic-voice'
#   cog provided in Rapptz discord.py repository (under the examples subdirectory)

import asyncio

import discord
import youtube_dl

from discord.ext import commands

#   Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

#   YT stream options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # ipv4 address only
}

ffmpeg_options = {
    'options': '-vn',
    'executable': 'ffmpeg'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

#   Youtube download source class (with FFmpeg audio conversion)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music:
    def __init__(self, bot):
        self.bot = bot

    #   Summon to voice channel
    @commands.command()
    async def summon(self, ctx, *arg):
        """Joins a voice channel"""
        
        #   Connect to a supplied voice channel
        if len(arg) != 0:
            channel = discord.utils.get(ctx.guild.voice_channels, name=arg[0])

            if channel is not None:
                if ctx.voice_client is not None:
                    return await ctx.voice_client.move_to(channel)

                await channel.connect()

        #   No input implies connect to users current voice channel
        else: 
            await ctx.author.voice.channel.connect()

    #   Play audio locally stored
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    #   Download first from YT and play
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    #   Stream (no local storage) Youtube audio
    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    #   Alter volume of audio
    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        
        if volume in range(1,101):
            if ctx.voice_client is None:
                return await ctx.send("Not connected to a voice channel.")

            ctx.voice_client.source.volume = volume/100
            await ctx.send("Changed volume to {}%".format(volume))

    #   Leave the discord channel (also stops audio)
    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
    
    #   Pause current audio stream
    @commands.command()
    async def pause(self,ctx):
        """Pauses current playback"""

        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
    
    #   Resume current audio stream
    @commands.command()
    async def resume(self, ctx):
        """Resumes current playback if paused"""
        
        ctx.voice_client.resume()

    #   Checks made on selection command before invocation
    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    #   Checks playback commands for proper invocation 
    @pause.before_invoke
    @resume.before_invoke
    @leave.before_invoke
    async def ensure_user_presence(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

#   discord.py requires this function to integrate the class (and subsequent methods) 
def setup(bot):
    bot.add_cog(Music(bot))