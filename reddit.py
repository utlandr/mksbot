import praw
import yaml
import random

def hot_copypasta(n_posts = 10):
    reddit = reddit_instance()
    subreddit = reddit.subreddit("copypasta")

    hot_pasta = subreddit.hot(limit=n_posts)

    for submission in hot_pasta:
        if len(submission.selftext) < 2000:
            submission.hide()
            return(submission.title,submission.selftext)

def reddit_instance():
    config = yaml.safe_load(open("./config.yml"))
    reddit = praw.Reddit(   client_id = config["copypasta"]["id"],
                            client_secret = config["copypasta"]["secret"],
                            user_agent = config["copypasta"]["user_agent"],
                            username = config["copypasta"]["username"],
                            password = config["copypasta"]["pw"]
                        )
    return reddit

def clear_hidden(n=None):
    reddit = reddit_instance()

    while True:
        posts = [post for post in reddit.user.me().hidden(limit=n)]
        if not posts:
            break
        posts[0].unhide(other_submissions=posts[1:len(posts)])
