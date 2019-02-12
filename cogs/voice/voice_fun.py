import asyncio

import discord


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

