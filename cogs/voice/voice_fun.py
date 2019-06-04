import asyncio
from emoji import demojize
import random
import wave
import discord
import yaml
import youtube_dl

#   Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

#   Import yaml configs
voice_config = yaml.safe_load(open("cogs/voice/voice_config.yml"))

#   droid_speak config
droid_speak_config = voice_config["droid_speak"]

#   YT stream options
ytdl_format_options = voice_config["youtube_dl_config"]
ffmpeg_options = voice_config["ffmpeg_config"]

#   Set the random seed
random.seed(31)


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
    """Play update audio when leaving/entering channels

    :param ctx: command invocation message context:
    :param state: specifies whether the bot is entering or leaving
    :return: None
    """
    if ctx.voice_client:
        if state == "Entering":
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(droid_speak_config["enter_audio"]))
            await asyncio.sleep(0.5)
            if ctx.voice_client.is_playing():
                ctx.voice_client.source = source
            else:
                ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        else:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(droid_speak_config["left_audio"]))
            if ctx.voice_client.is_playing():
                ctx.voice_client.source = source
            else:
                ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await asyncio.sleep(1.7)


async def add_queue(music, ctx, player):
    """Add player to a music queue

    :param music: The bot's Music cog instance
    :param ctx: command invocation message context
    :param player: the music player object
    :return: None
    """
    guild_id = ctx.message.guild.id
    music.queues[guild_id].append(player)
    await ctx.send(embed=create_queued_embed(player, len(music.queues[guild_id])))


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
            asyncio.run_coroutine_threadsafe(ctx.send(embed=create_playing_embed(player, "Playing")),
                                             loop=music.bot.loop)
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


def format_duration(duration):
    """

    :param duration: integer time in seconds
    :return: formatted minute:second time string
    """
    formatted = "{:02d}:{:02d}".format(round(duration / 60), duration % 60)

    return formatted


def create_playing_embed(source, status):
    """Generate a playing embed source

    :param source: The audio player source object
    :param status: Verbose description of the players status
    :return: a discord.Embed object containing player information
    """
    if source.data["is_live"]:
        duration = "LIVE"

    else:
        duration = format_duration(source.data["duration"])

    embed_playing = discord.Embed(
        title=" ",
        description=" ",
        color=0xeee657)

    embed_playing.set_author(
        name="MksBot Player - Now Playing",
        url="https://github.com/utlandr/mksbot",
        icon_url="https://upload.wikimedia.org/wikipedia/commons/8/88/45_rpm_record.png")

    embed_playing.add_field(
        name="Audio",
        value="[{}]({})".format(source.title, source.data["webpage_url"]),
        inline=False)

    embed_playing.add_field(
        name="Duration",
        value=duration,
        inline=False)

    embed_playing.add_field(
        name="Status",
        value=status)

    embed_playing.set_thumbnail(url=source.data["thumbnail"])

    return embed_playing


def create_queued_embed(source, position):
    """Generate a queued audio embed

    :param source: The audio player source object
    :param position: THe position in the queue
    :return:
    """
    if source.data["is_live"]:
        duration = "LIVE"

    else:
        duration = format_duration(source.data["duration"])

    embed_queued = discord.Embed(title=" ",
                                 description=" ",
                                 color=0xeee657)

    embed_queued.set_author(name="MksBot Player - Queued Audio",
                            url="https://github.com/utlandr/mksbot",
                            icon_url="https://upload.wikimedia.org/wikipedia/commons/8/88/45_rpm_record.png")

    embed_queued.add_field(name="Audio",
                           value="[{}]({})".format(source.title, source.data["webpage_url"]),
                           inline=False)

    embed_queued.add_field(name="Duration",
                           value=duration,
                           inline=False)

    embed_queued.add_field(name="Status",
                           value="Queued: {}".format(int_to_ordinal(position)))

    embed_queued.set_thumbnail(url=source.data["thumbnail"])

    return embed_queued


def int_to_ordinal(num):
    """Convert int value to ordinal string

    :param num: Integer
    :return:pu String representing the translated ordinal
    """
    if num > 9:
        second_last = str(num)[-2]
        if second_last == "1":
            append = "th"
            return "{}{}".format(num, append)

    last = num % 10
    if last == 1:
        append = "st"
    elif last == 2:
        append = "nd"
    elif last == 3:
        append = "rd"
    else:
        append = "th"

    return "{}{}".format(num, append)


async def droid_speak_translate(ctx, phrase):
    """Translates user supplied text into droid speak audio that the bot will speak in a voice channel

    :param ctx: command invocation message context
    :param phrase: String containing user supplied text
    :return: None
    """

    infiles = list()
    char_tot = 0

    for word in phrase:
        char_tot += len(word)
        if char_tot > droid_speak_config["char_limit"]:
            break

        elif demojize(word) in droid_speak_config["emoji"].keys():
            infiles.append(droid_speak_config["emoji"][demojize(word)])

        elif word in droid_speak_config["special"].keys():
            infiles.append(droid_speak_config["special"][word])

        else:
            random.seed(unique_num(word))
            s_size = len(word) if len(word) < 3 else 3
            addon = random.sample(list(droid_speak_config["alphabet"].keys()), k=s_size)

            for c in addon:
                if c in droid_speak_config["alphabet"].keys():
                    infiles.append(droid_speak_config["alphabet"][c])

                elif c is "space":
                    infiles.append(droid_speak_config["space"])

        infiles.append(droid_speak_config["space"])

    if infiles:
        wav_params = list()
        wav_params.append(droid_speak_config["header"]["nchannels"])
        wav_params.append(droid_speak_config["header"]["sampwidth"])
        wav_params.append(droid_speak_config["header"]["framerate"])
        wav_params.append(droid_speak_config["header"]["nframes"])
        wav_params.append(droid_speak_config["header"]["comptype"])
        wav_params.append(droid_speak_config["header"]["compname"])

        outfile = "./audio/output/sounds.wav"

        with wave.open(outfile, "wb") as output:
            output.setparams(wav_params)
            for infile in infiles:
                with wave.open(infile, 'rb') as w:
                    data = [[w.getparams(), w.readframes(w.getnframes())]]
                    output.writeframes(data[0][1])

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(outfile))
        ctx.voice_client.play(source)


def unique_num(s):
    """Transform a string into a 'unique' integer value

    :param s: string to convert
    :return ret: unique integer value
    """
    ret = 0

    for i, j in enumerate(s):
        ret += ord(j) << (i * 8)

    return ret
