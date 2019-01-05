import praw
import random
import yaml
from discord import Embed

def reddit_post(sub, sort_by, n_posts = 100):
    """Scrapes reddit for hot posts"""
    reddit = reddit_instance()
    subreddit = reddit.subreddit(sub)

    if sub != "all":
        try:
            subreddit.id
        
        except Exception as e:
            print("Error: %s"%e)
            return("r/%s not found"%sub, None)

    #   Grab a list of non-hidden (unread) posts
    post_list = subreddit.hot(limit=n_posts)

    #   Return a submission that hasn't previously been shown, hide posts that don't meet embedded criteria
    for submission in post_list:
        if (len(submission.selftext)) < 2048 and len(submission.title) < 256 and not submission.stickied:
            submission.hide()
            return(submission)

        else:
            submission.hide()

def reddit_embed(submission):
    """Converts a raw submission into a pretty discord embedded message"""

    embedded = Embed(title = submission.title, description = submission.selftext, url=submission.shortlink).set_footer(text="Submitted by:\tu/%s"%submission.author)

    return(embedded)

def reddit_instance():
    """Setup the reddit connection (to bot account)"""
    config = yaml.safe_load(open("config.yml"))
    reddit = praw.Reddit(   client_id = config["reddit"]["id"],
                            client_secret = config["reddit"]["secret"],
                            user_agent = config["reddit"]["user_agent"],
                            username = config["reddit"]["username"],
                            password = config["reddit"]["pw"]
                        )
    return reddit

def clear_hidden(n=None):
    """An external function to clear all read/hidden posts on the bot account"""
    reddit = reddit_instance()

    while True:
        posts = [post for post in reddit.user.me().hidden(limit=n)]
        if not posts:
            break
        posts[0].unhide(other_submissions=posts[1:len(posts)])