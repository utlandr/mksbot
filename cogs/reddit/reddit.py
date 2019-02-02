import asyncio
import yaml

import discord
from discord.ext import commands
from cogs.reddit_fun import reddit_embed
from cogs.reddit_fun import reddit_post


#   Reddit cog for all things Reddit
class Reddit:
    def __init__(self, bot):
        self.bot = bot
        self.config = yaml.safe_load(open("config.yml"))
    
    #   copypasta scrapes hot comments from r/copypasta subreddit using PRAW
    @commands.command(pass_context=True)
    async def reddit(self, ctx, subreddit="all", sort_by="hot"):
        """Scrape and send a formatted post from any subreddit

        :param ctx: command invocation message context
        :param subreddit: a subreddit to scrape posts from
        :param sort_by: ordering of post list to retrieve
        :return: None
        """
        
        async with ctx.typing():
            submission = reddit_post(subreddit, sort_by)
            reddit_response, tack_on = reddit_embed(submission)
            reddit_response.colour = self.config["reddit"]["response_colour"]

        await ctx.send(embed=reddit_response)
        if tack_on.startswith("https://streamable"):
            await asyncio.sleep(5)
        await ctx.send(tack_on)


#   This function is used by discord.py to integrate the cog+subroutines into the bot
def setup(bot):
    bot.add_cog(Reddit(bot))
