import asyncio
import yaml

from discord.ext import commands
from cogs.reddit.reddit_fun import clear_hidden
from cogs.reddit.reddit_fun import reddit_embed
from cogs.reddit.reddit_fun import reddit_post


#   Reddit cog for all things Reddit
class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = yaml.safe_load(open("config.yml"))

    @commands.command(pass_context=True)
    async def reddit(self, ctx, subreddit="all", sort_by="hot"):
        """Scrape and send a formatted post from any subreddit

        :param ctx: command invocation message context
        :param subreddit: a subreddit to scrape posts from
        :param sort_by: ordering of post list to retrieve
        :return: None
        """
        # Retrieve post
        async with ctx.typing():
            submission = reddit_post(subreddit, sort_by)
            reddit_response, tack_on = reddit_embed(submission)
            reddit_response.colour = self.config["reddit"]["response_colour"]

            # If an additional gif/video from the post is required
            if tack_on:
                # Streamable takes some time to process
                if tack_on.startswith("https://streamable"):
                    await asyncio.sleep(5)

                await ctx.send(embed=reddit_response)    
                await ctx.send(tack_on)

            else:
                await ctx.send(embed=reddit_response)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def reddit_clear(self, ctx, posts=10):
        """Clears a specified number of posts from the reddit account hidden set

        :param ctx: command invocation message context
        :param posts: number of posts to remove
        :return: None
        """
        clear_hidden(posts)
        await ctx.send("Posts successfully unhidden")


#   This function is used by discord.py to integrate the cog+subroutines into the bot
def setup(bot):
    bot.add_cog(Reddit(bot))
