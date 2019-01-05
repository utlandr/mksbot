import discord
import yaml
from discord.ext import commands
from cogs.reddit_fun import *

#   Reddit cog for all things Reddit
class Reddit:
    def __init__(self, bot):
        self.bot = bot
        self.config = yaml.safe_load(open("config.yml"))
    
    #   copypasta scrapes hot comments from r/copypasta subreddit using PRAW
    @commands.command(pass_context=True)
    async def reddit(self, ctx, subreddit="all", sort_by="hot"):
        """Scrape and send a formatted post from any subreddit"""
        
        async with ctx.typing():
            submission = reddit_post(subreddit,sort_by)
            reddit_response = reddit_embed(submission)#discord.Embed(title = submission.title, description = submission.selftext, color = self.config["copypasta"]["response_colour"])
            reddit_response.colour=self.config["reddit"]["response_colour"]
            #reddit_response.set_author(name= "Submitted By:\t%s"%submission.author, url = submission.shortlink)
        await ctx.send(embed = reddit_response)

#   This function is used by discord.py to integrate the cog+subroutines into the bot
def setup(bot):
    bot.add_cog(Reddit(bot))