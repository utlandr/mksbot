import discord
import yaml
from discord.ext import commands
from cogs.reddit_fun import hot_copypasta

'''Reddit cog for all things Reddit'''
class Reddit:
    def __init__(self, bot):
        self.bot = bot
        self.config = yaml.safe_load(open("config.yml"))
    
    #   copypasta scrapes hot ocmments from r/copypasta subreddit using PRAW
    @commands.command(pass_context=True)
    async def copypasta(self, ctx):
        title,content = hot_copypasta(5)
        pasta_response = discord.Embed(title = title, description = content, color = self.config["copypasta"]["response_colour"])
        await ctx.send(embed = pasta_response)

def setup(bot):
    bot.add_cog(Reddit(bot))