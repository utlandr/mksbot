import praw
import random
import yaml


def hot_copypasta(n_posts = 10):
    """Scrapes r/copypasta for material"""
    reddit = reddit_instance()
    subreddit = reddit.subreddit("copypasta")

    #   Grab top ten posts in the hot section
    hot_pasta = subreddit.hot(limit=n_posts)

    #   Return a submission that hasn't previously been shown
    for submission in hot_pasta:
        if len(submission.selftext) < 2000:
            submission.hide()
            return(submission.title,submission.selftext)

def reddit_instance():
    """Setup the reddit connection (to bot account)"""
    config = yaml.safe_load(open("config.yml"))
    reddit = praw.Reddit(   client_id = config["copypasta"]["id"],
                            client_secret = config["copypasta"]["secret"],
                            user_agent = config["copypasta"]["user_agent"],
                            username = config["copypasta"]["username"],
                            password = config["copypasta"]["pw"]
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
