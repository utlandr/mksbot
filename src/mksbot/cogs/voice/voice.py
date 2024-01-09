from typing import Any

import discord
from discord import Message, Reaction, User, VoiceClient
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot
from discord.member import Member
from discord.player import PCMVolumeTransformer

from mksbot.cogs.voice.voice_fun import (
    YTDLSource,
    YTVideo,
    add_queue,
    bot_audible_update,
    create_queue_embed,
    droid_speak_translate,
    format_duration,
    play_queue,
    setup_player,
)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.def_volume = 0.05
        self.cur_volume = self.def_volume
        self.queues: dict[int, list[YTVideo]] = {}
        self.players: dict[int, PCMVolumeTransformer[Any]] = {}

    #   Summon to voice channel
    @commands.command()
    async def summon(self, ctx: commands.Context[Any], *arg: list[str]) -> None:
        """Joins a voice channel

        :param ctx: command invocation message context
        :param arg:
        :return: None
        """

        #   Connect to a supplied voice channel
        if len(arg) != 0:
            guild = ctx.guild
            if guild:
                channel = discord.utils.get(guild.voice_channels, name=arg[0])

                if channel is not None:
                    if ctx.voice_client is not None:
                        await ctx.bot.voice_clients[0].move_to(channel)
                        return

                    await channel.connect()
                    await bot_audible_update(ctx, "Entering")

        #   No input implies connect to users current voice channel
        else:
            author = ctx.author
            assert isinstance(author, Member)
            voice = author.voice
            if voice:
                channel_act = voice.channel
                voice_client = ctx.bot.voice_clients[0]
                if voice_client:
                    await voice_client.move_to(channel_act)
                else:
                    if channel_act:
                        await channel_act.connect()
                        await bot_audible_update(ctx, "Entering")

    #   Leave the discord channel (also stops audio)
    @commands.command()
    async def leave(self, ctx: Context[Any]) -> None:
        """Stops and disconnects the bot from voice

        :param ctx: command invocation message context
        :return: None
        """

        await bot_audible_update(ctx, "Leaving")
        if ctx.message.guild:
            guild_id = ctx.message.guild.id
            if guild_id in self.queues:
                q = self.queues.get(guild_id, None)
                if q:
                    del q[:]

            await ctx.bot.voice_clients[0].disconnect()

    #   Stream (no local storage) Youtube audio
    @commands.command()
    async def stream(self, ctx: Context[Any], *, url: str) -> None:
        """Streams from a url (same as yt, but doesn't predownload)

        :param ctx: command invocation message context
        :param url: YouTube video URL
        :return:
        """
        async with ctx.typing():
            source = await YTDLSource.get_info(url)
            vc = ctx.bot.voice_clients[0]
            if source.videos:
                await add_queue(self, ctx, source)
            else:
                await ctx.send("Media not found.")

        if vc.is_paused() or vc.is_playing():
            pass
        else:
            play_queue(self, ctx)

    #   Alter volume of audio
    @commands.command()
    async def volume(self, ctx: Context[Any], *volume: int) -> Message:
        """Changes the player's volume

        :param ctx: command invocation message context
        :param volume: volume to set the player to
        :return: message reply on successful volume update
        """

        try:
            bot_volume = int(ctx.bot.voice_clients[0].source.volume * 100)

        except AttributeError:
            perc_vol = self.def_volume * 100
            msg = "Audio not initialized\nDefault audio volume is {}%".format(perc_vol)
            return await ctx.send(msg)

        if volume:
            if volume[0] in range(1, 101) and volume[0] != bot_volume:
                if ctx.voice_client is None:
                    return await ctx.send("You are not connected to a voice channel.")

                ctx.bot.voice_clients[0].source.volume = volume[0] / 100
                self.cur_volume = volume[0] / 100
                return await ctx.send("Changed volume to {}%".format(int(volume[0])))

        return await ctx.send("Current volume is {}%".format(bot_volume))

    @commands.command()
    async def flick(self, ctx: Context[Any]) -> None:
        """Switch between paused and playing states

        :param ctx: command invocation message context
        :return: None
        """
        voice_client = ctx.bot.voice_clients[0]
        if voice_client.is_playing():
            voice_client.pause()
        elif voice_client.is_paused():
            voice_client.resume()

    async def _react_flick(self) -> None:
        """Switch between paused and playing states

        :param reaction: Reaction object invoking flick action
        :return: None
        """
        vc = self.bot.voice_clients[0]
        assert isinstance(vc, VoiceClient)
        if vc:
            if vc.is_playing():
                vc.pause()
            elif vc.is_paused():
                vc.resume()

    #   Pause current audio stream
    @commands.command()
    async def pause(self, ctx: Context[Any]) -> None:
        """Pauses current playback

        :param ctx: command invocation message context
        :return: None
        """
        vc = ctx.bot.voice_clients[0]
        assert isinstance(vc, VoiceClient)

        if vc.is_playing():
            vc.pause()

    #   Resume current audio stream
    @commands.command()
    async def resume(self, ctx: Context[Any]) -> None:
        """Resumes current playback if paused

        :param ctx: command invocation message context
        :return: None
        """
        ctx.bot.voice_clients[0].resume()

    #   Skip current song and play the next one
    @commands.command()
    async def skip(self, ctx: Context[Any], *queue_id: int | str) -> None:
        """Skips current player and plays the next player in the queue

        :param ctx: command invocation message context
        :param queue_id: 1-based queue index to remove player
        :return:
        """
        guild = ctx.message.guild
        vc = ctx.bot.voice_channel[0]
        if guild:
            guild_id = guild.id
            if queue_id:
                if queue_id[0] == "all":
                    del self.queues[guild_id][:]
                    vc.stop()
                    await ctx.send("Queue has been emptied.")
                elif int(queue_id[0]) and int(queue_id[0]) <= len(self.queues[guild_id]):
                    removed = self.queues[guild_id].pop(int(queue_id[0]) - 1).title
                    await ctx.send("Removed:\t{}".format(removed))
            else:
                player_title = self.queues[guild_id][0].title
                await ctx.send("Skipping:\t{}".format(player_title))
                vc.stop()

    async def _react_skip(self, reaction: Reaction) -> None:
        guild = reaction.message.guild
        if guild:
            guild_id = guild.id
            player_title = self.queues[guild_id][0].title
            await reaction.message.channel.send("Skipping:\t{}".format(player_title))
            vc = self.bot.voice_clients[0]
            assert isinstance(vc, VoiceClient)
            vc.stop()

    #   Display information about current audio being played
    @commands.command()
    async def player(self, ctx: Context[Any]) -> None:
        """Display information about current audio being played

        :param ctx: command invocation message context
        :return:
        """
        guild = ctx.guild
        vc = ctx.bot.voice_channels[0]
        if guild:
            guild_id = guild.id
            queue = self.queues[guild_id]
            if vc ^ queue:
                source = queue[0]
                await setup_player(ctx, source)

    #   View the queue of the existing playlist
    @commands.command()
    async def queue(self, ctx: Context[Any], first: int = 5) -> None:
        """

        :param ctx: command invocation message context
        :param first: the number of audio sources to display in the embed
        :return:
        """
        guild = ctx.guild
        if guild:
            guild_id = guild.id
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

                    queue_string += "{0}. {1} | [{2}](https://youtube.com/watch?v={3})\n\n".format(
                        playlist_id, duration, aud_source.title, aud_source.id
                    )
                    count += 1

                embed_queue.add_field(name="Total in Queue", value=len(queue_cp))
                embed_queue.add_field(name="\u200b", value="\u200b", inline=False)
                embed_queue.add_field(
                    name=f"Queue (Displaying first {first})",
                    value=queue_string,
                    inline=False,
                )
                ret_msg: Message = await ctx.send(embed=embed_queue)
                await ret_msg.delete(delay=10)

    @commands.command()
    async def speak(self, ctx: Context[Any], *phrase: str) -> None:
        """Have the bot translate a phrase into Droidspeak

        :param ctx: command invocation message context
        :return: None
        """
        vc = ctx.bot.voice_clients[0]
        if not vc.is_playing() or vc.is_paused():
            await droid_speak_translate(ctx, list(phrase))

    @staticmethod
    def _is_not_bot(user: User) -> bool:
        return not user.bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User) -> None:
        """Listen for all added reactions

        :param reaction: Reaction that was submitted by a User
        :param user: The User that submitted the Reaction
        :return:
        """
        if self._is_not_bot(user):
            await self.manage_music(reaction, user)

    async def manage_music(self, reaction: Reaction, user: User) -> None:
        """For a given Reaction, determine if music player needs to be managed

        :param reaction: a Reaction object
        :param user: the User who sent the Reaction
        :return:
        """
        if reaction.message.author.bot:  # This loosely rules out reactions to non-bot messages messages.
            if str(reaction) == "⏭️":
                await self._react_skip(reaction)
                await reaction.message.clear_reactions()
                await reaction.message.delete(delay=10)
            elif str(reaction) == "⏯️":
                await self._react_flick()
                await reaction.remove(user)
            else:
                pass

    @stream.before_invoke
    @speak.before_invoke
    async def ensure_voice(self, ctx: Context[Any]) -> None:
        """Checks made on selection command before invocation

        :param ctx: command invocation message context
        :return:
        """
        if ctx.voice_client is None:
            assert isinstance(ctx.author, Member)
            if ctx.author.voice:
                ch = ctx.author.voice.channel
                if ch:
                    await ch.connect()
                    await bot_audible_update(ctx, "Entering")
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

    #   Checks playback commands for proper invocation
    @pause.before_invoke
    @resume.before_invoke
    @skip.before_invoke
    @leave.before_invoke
    async def ensure_user_presence(self, ctx: Context[Any]) -> None:
        if ctx.voice_client is None:
            assert isinstance(ctx.author, Member)
            if ctx.author.voice:
                ch = ctx.author.voice.channel
                if ch:
                    await ch.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")


async def setup(bot: Bot) -> None:
    await bot.add_cog(Music(bot))
