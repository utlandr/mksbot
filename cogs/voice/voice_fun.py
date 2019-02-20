import asyncio

import discord
import youtube_dl

#   Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

#   YT stream options
ytdl_format_options = {'format': 'bestaudio/best',
                       'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                       'restrictfilenames': True,
                       'noplaylist': True,
                       'nocheckcertificate': True,
                       'ignoreerrors': True,
                       'logtostderr': False,
                       'quiet': True,
                       'no_warnings': True,
                       'default_search': 'auto',
                       'source_address': '0.0.0.0',  # ipv4 address only
                       'buffer_size': '16K',
                       }

ffmpeg_options = {'options': '-vn',
                  'executable': 'ffmpeg',
                  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
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
        """Stream audio from a supplied url instead of searching

        :param url: supplied URL
        :param loop: video looping
        :param stream: determine if URL is a stream
        :return:
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


async def bot_audible_update(ctx, state):
    """Play TTS (text to speech) audio specifying the bot leaving/entering a voice channel

    :param ctx: command invocation message context:
    :param state: string specifying whether the bot is entering or leaving the channel
    :return: None
    """
    if ctx.voice_client:
        if state is "Entering":
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("./audio/mksbot_enter.wav"))
            await asyncio.sleep(0.5)
            if ctx.voice_client.is_playing():
                ctx.voice_client.source = source
            else:
                ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        else:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("./audio/mksbot_left.wav"))
            if ctx.voice_client.is_playing():
                ctx.voice_client.source = source
            else:
                ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await asyncio.sleep(1.7)


async def queue(music, ctx, player):
    """Add player to a music queue

    :param music: The bot's Music cog instance
    :param ctx: command invocation message context
    :param player: the music player object
    :return: None
    """
    guild = ctx.message.guild
    music.queues[guild.id].append(player)
    response = "Audio Queued:\t{}".format(player.title)
    await ctx.send(response)


#   Queue player
def play_queue(music, ctx):
    """Pops the first player item in the music queue and plays it

    :param music: The bot's Music cog instance
    :param ctx: command invocation message context
    :return: None
    """
    guild_id = ctx.message.guild.id
    if check_queue(music.queues, ctx.message.guild.id):
        if len(music.queues[guild_id]):
            player = music.queues[guild_id].pop(0)
            music.players[guild_id] = player

            ctx.voice_client.play(player, after=lambda e: print(e) if e else play_queue(music, ctx))
            ctx.voice_client.source.volume = music.cur_volume
            asyncio.run_coroutine_threadsafe(ctx.send("Now playing:\t{}".format(player.title)), loop=music.bot.loop)
        else:
            pass


def check_queue(c_queue, c_id):
    """Check specified queue for guild id

    :param c_queue: The queue (dictionary) to check
    :param c_id: The guild ID to check
    :return:
    """
    if c_queue[c_id] is not []:
        return True
    else:
        return False
