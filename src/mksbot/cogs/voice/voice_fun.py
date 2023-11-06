import asyncio
import random
import re
import wave

import discord
import googleapiclient.discovery
import yaml
import youtube_dl
from discord import Message
from emoji import demojize

#   Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""

#   Import configs
voice_config = yaml.safe_load(open("src/mksbot/cogs/voice/voice_config.yml"))
yt_api = yaml.safe_load(open("config.yml"))["youtube_data_api"]
droid_speak_config = voice_config["droid_speak"]
ytdl_format_options = voice_config["youtube_dl_config"]
ffmpeg_options = voice_config["ffmpeg_config"]

#   Set the random seed
random.seed(31)

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
youtube = googleapiclient.discovery.build(
    yt_api["api_service_name"], yt_api["api_version"], developerKey=yt_api["api_key"]
)


#   Youtube download source class (with FFmpeg audio conversion)
class YTDLSource:
    def __init__(self, data, videos):
        self.data = data
        self.request_type = data.get("kind")
        self.request = data.get("")
        self.videos = videos

    @classmethod
    async def get_info(cls, url):
        """Stream audio from a supplied url instead of searching

        :param url: supplied URL
        :return:
        """

        data = {}
        videos = []

        # Identify video/playlist/search-query request.
        video_search = re.search(yt_api.get("video_regex"), url)
        playlist_search = re.search(yt_api.get("playlist_regex"), url)

        if video_search:
            request = youtube.videos().list(part="snippet,contentDetails", id=video_search.group(1))
        elif playlist_search:
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_search.group(1),
                maxResults=50,
            )
        else:
            request = youtube.search().list(part="snippet", q=url, maxResults=1, type="video")
        response = request.execute()
        data["request"] = url
        data["request_type"] = response.get("kind")

        # Generate video information instances
        for item in response.get("items"):
            info = item
            if item.get("kind") == "youtube#searchResult":
                vid_request = youtube.videos().list(part="snippet, contentDetails", id=item.get("id").get("videoId"))
                info = vid_request.execute()
                videos.append(YTVideo(info.get("items")[0]))
            elif item.get("kind") == "youtube#playlistItem":
                info = (
                    youtube.videos()
                    .list(
                        part="snippet,contentDetails",
                        id=item.get("contentDetails").get("videoId"),
                    )
                    .execute()
                )
                if info.get("items"):
                    videos.append(YTVideo(info.get("items")[0]))

            else:
                videos.append(YTVideo(info))

        return cls(data, videos)


class YTVideo:
    def __init__(self, entry: dict):
        self.title = entry.get("snippet").get("title")
        self.id = entry.get("id")
        self.duration = entry.get("contentDetails").get("duration")
        self.channel_name = entry.get("snippet").get("channelTitle")
        self.channel_id = entry.get("snippet").get("channelId")
        self.thumbnail_url = entry.get("snippet").get("thumbnails").get("default").get("url")
        self.is_live = entry.get("liveBroadcastContent")

    def extract_audio(self):
        """Retrieve AudioSource from YT info

        :return:
        """
        url = f"https://www.youtube.com/watch?v={self.id}"
        ytdl.cache.remove()
        data = ytdl.extract_info(url, download=False)

        filename = data["url"]

        tmp = discord.FFmpegPCMAudio(filename, **ffmpeg_options)
        return tmp


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
                ctx.voice_client.play(source, after=lambda e: print("Player error: %s" % e) if e else None)

        else:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(droid_speak_config["left_audio"]))
            if ctx.voice_client.is_playing():
                ctx.voice_client.source = source
            else:
                ctx.voice_client.play(source, after=lambda e: print("Player error: %s" % e) if e else None)
            await asyncio.sleep(1.7)


async def add_queue(music, ctx, source: YTDLSource):
    """Add source to a music queue

    :param music:
    :param ctx:
    :param source:
    :return:
    """
    guild_id = ctx.message.guild.id
    if guild_id in music.queues:
        music.queues[guild_id].extend(source.videos)

    else:
        music.queues[guild_id] = source.videos

    if len(source.videos) == 1:
        embed = single_queue_embed(source.videos[0], len(music.queues[guild_id]))
        ret_msg: Message = await ctx.send(embed=embed)
        await ret_msg.delete(delay=10)
    else:
        embed = playlist_queue_embed(source)
        ret_msg: Message = await ctx.send(embed=embed)
        await ret_msg.delete(delay=10)
    return


async def setup_player(ctx, source):
    msg = await ctx.send(embed=create_playing_embed(source, "Playing"))
    await msg.add_reaction("⏯️")
    await msg.add_reaction("⏭️")


#   Queue player
def play_queue(music, ctx):
    """Setup and manage the music player

    :param music: The bot's Music cog instance
    :param ctx: command invocation message context
    :return: None
    """
    guild_id = ctx.message.guild.id
    if ctx.voice_client:
        if ctx.voice_client.is_paused() or ctx.voice_client.is_playing():
            pass
        else:
            if check_queue(music.queues, ctx.message.guild.id):
                if len(music.queues[guild_id]):
                    source = music.queues[guild_id][0]
                    tmp = source.extract_audio()
                    audio = discord.PCMVolumeTransformer(tmp, volume=music.cur_volume)
                    music.players[guild_id] = audio
                    asyncio.run_coroutine_threadsafe(setup_player(ctx, source), loop=music.bot.loop)
                    play_audio(music, audio, ctx)
                else:
                    pass


def play_audio(music, source, ctx):
    ctx.voice_client.play(source, after=lambda e: print(e) if e else on_audio_complete(music, ctx))


def on_audio_complete(music, ctx):
    guild_id = ctx.message.guild.id
    music.queues[guild_id].pop(0)

    if ctx.voice_client:
        play_queue(music, ctx)


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


def create_queue_embed(title):
    """Generates the base embed information for !queue command

    :param title: embed title
    returns: a discord.Embed object that contains base queue infoqueued
    """
    playlist_embed = discord.Embed(title=" ", description=" ", color=0xEEE657)

    playlist_embed.set_author(
        name=title,
        url=voice_config["info"]["source_code"],
        icon_url=voice_config["info"]["image"],
    )

    return playlist_embed


def format_duration(duration):
    """

    :param duration: ISO8601 formatted time delta
    :return: formatted 'h m s' time string
    """
    formatted = re.sub(r"\B([A-Z])", r"\1 ", duration.replace("PT", "")).lower()

    return formatted


def create_playing_embed(source: YTVideo, status):
    """Generate a playing embed source

    :param source: The audio player source object
    :param status: Verbose description of the players status
    :return: a discord.Embed object containing player information
    """
    if source.is_live:
        duration = "LIVE"

    else:
        duration = format_duration(source.duration)

    embed_playing = discord.Embed(title=" ", description=" ", color=0xEEE657)

    embed_playing.set_author(
        name="MksBot Player - Now Playing",
        url=voice_config["info"]["source_code"],
        icon_url=voice_config["info"]["image"],
    )

    embed_playing.add_field(
        name="Audio",
        value="[{}](https://www.youtube.com/watch?v={})".format(source.title, source.id),
        inline=False,
    )

    embed_playing.add_field(name="Duration", value=duration, inline=False)

    embed_playing.add_field(name="Status", value=status)

    embed_playing.set_thumbnail(url=source.thumbnail_url)

    return embed_playing


def single_queue_embed(video: YTVideo, position):
    """Generate a queued audio embed

    :param video: YTVideo source
    :param position: THe position in the queue
    :return:
    """
    if video.is_live:
        duration = "LIVE"

    else:
        duration = format_duration(video.duration)

    playlist_embedd = discord.Embed(title=" ", description=" ", color=0xEEE657)

    playlist_embedd.set_author(
        name="MksBot Player - Queued Audio",
        url=voice_config["info"]["source_code"],
        icon_url=voice_config["info"]["image"],
    )

    playlist_embedd.add_field(
        name="Audio",
        value=f"[{video.title}](https://www.youtube.com/watch?v={video.id})",
        inline=False,
    )

    playlist_embedd.add_field(name="Duration", value=duration, inline=False)

    playlist_embedd.add_field(name="Status", value="Queued: {}".format(int_to_ordinal(position)))

    playlist_embedd.set_thumbnail(url=video.thumbnail_url)

    return playlist_embedd


def playlist_queue_embed(source: YTDLSource):
    """Generates an Embed object for added playlists

    :param source: the YTDLSource object containing playlist information
    :return: Embed object
    """
    playlist_embed = create_queue_embed(title="MksBot Player - Queued Playlist")

    playlist_embed.add_field(name="Playlist Added", value=source.data.get("request"))
    playlist_embed.add_field(name="\u200b", value="\u200b", inline=False)
    playlist_embed.add_field(name="Tracks Added", value=f"{len(source.videos)}", inline=False)

    return playlist_embed


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

                elif c == "space":
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
                with wave.open(infile, "rb") as w:
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
