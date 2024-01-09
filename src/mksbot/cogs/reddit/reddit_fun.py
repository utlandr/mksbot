import praw
import yaml
from discord import Embed
from praw.models import Submission

from mksbot.cogs.voice.streamable import streamable_instance, upload_streamable


def reddit_post(sub: str, sort_by: str, n_posts: int = 100) -> Submission:
    """Scrapes reddit for hot posts

    :param sub: subreddit name to scrape posts
    :param sort_by: reddit posts ordering
    :param n_posts: number of posts to retrieve
    :return: a selected praw.Submission object
    """
    reddit = reddit_instance()
    subreddit = reddit.subreddit(sub)

    if sub != "all":
        try:
            subreddit.id

        except Exception as e:
            print("Error: {}".format(e))
            raise ValueError("r/{} not found".format(sub)) from e

    #   Grab a list of non-hidden (unread) posts
    if sort_by == "hot":
        post_list = subreddit.hot(limit=n_posts)

    elif sort_by == "new":
        post_list = subreddit.new(limit=n_posts)

    elif sort_by == "top":
        post_list = subreddit.top(limit=n_posts)

    else:
        post_list = subreddit.hot(limit=n_posts)

    #   Return a submission that hasn't previously been shown, hide posts that don't meet embedded criteria
    for submission in post_list:
        if (len(submission.selftext)) < 2048 and len(submission.title) < 256 and not submission.stickied:
            submission.hide()
            return submission

        else:
            submission.hide()


def reddit_embed(submission: Submission) -> tuple[Embed, str]:
    """Converts a raw submission into a pretty discord embedded message

    :param submission: praw.Submission object
    :return embedded: discord.Embed object containing reddit post information
    :return tack_on: a string containing a URL to tack below (comment after) the embedding
    """

    #   Every post will contain base details/submission text
    embedded = Embed(
        title="{}\n{}\n\n".format(submission.subreddit_name_prefixed, submission.title),
        description=submission.selftext,
        url=submission.shortlink,
    ).set_footer(text="Submitted by:\tu/{}".format(submission.author))

    tack_on = ""

    #   image/gif format
    if hasattr(submission, "post_hint"):
        if submission.post_hint == "image":
            embedded.set_image(url=submission.url)

        elif submission.post_hint == "hosted:video" or submission.post_hint == "rich:video":
            embedded.description = submission.url
            if "v.redd.it" in submission.url:
                user, pw = streamable_instance()
                tack_on = "https://streamable.com/{}".format(upload_streamable(submission.url, user, pw))

            else:
                tack_on = submission.url

        elif submission.post_hint == "link":
            if submission.url.endswith(".gif") or submission.url.endswith(".gifv"):
                if "v.redd.it" in submission.url:
                    user, pw = streamable_instance()
                    tack_on = "https://streamable.com/{}".format(upload_streamable(submission.url, user, pw))
                else:
                    tack_on = submission.url

            else:
                embedded.set_image(url=submission.preview["images"][0]["resolutions"][-2]["url"])

    else:
        if submission.url.startswith("https://www.reddit.com/r"):
            embedded.description = submission.selftext

    return embedded, tack_on


def reddit_instance() -> praw.Reddit:
    """Setup the reddit connection (to bot account)

    :return: praw.Reddit instance
    """
    config = yaml.safe_load(open("config.yml"))
    reddit = praw.Reddit(
        client_id=config["reddit"]["id"],
        client_secret=config["reddit"]["secret"],
        user_agent=config["reddit"]["user_agent"],
        username=config["reddit"]["username"],
        password=config["reddit"]["pw"],
    )

    return reddit


def clear_hidden(n: int | None = None) -> None:
    """An external function to clear all read/hidden posts on the bot account"""
    reddit = reddit_instance()

    while True:
        posts = [post for post in reddit.user.me().hidden(limit=n)]
        if not posts:
            break
        posts[0].unhide(other_submissions=posts[1 : len(posts)])
