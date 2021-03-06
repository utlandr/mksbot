import asyncio
import codecs
import discord
import random


def get_random_donger():
    """Return a random line from a plaintext file

    :return: randomly selected string from file
    """

    lines = codecs.open('dongers.txt', encoding='utf-8').read().splitlines()
    myline = random.choice(lines)
    return myline


def russian_roulette(name, death_vals, count):
    """Returns the appropriate response to a russian roulette roll.

    :param name: targeted user name
    :param death_vals: list specifying values that will result in a 'kill'
    :param count: targeted user's assigned count value
    :return response: string response to send to as a reply
    :return hit: specifies whether user was 'killed' or not
    """

    if count in death_vals:
        response = "BOOOOM HEADSHOT, {} got pwned".format(name)
        hit = 1
    
    else:
        response = "CLICK, {} gets to live another round".format(name)
        hit = 0

    return response, hit


async def target_spam(target: discord.Member, spam_limit=10):
    """Spams the target member of the guild with several DMs

    :param target: discord.Member object to spam user with messages
    :param spam_limit: Maximum number of messages to spam the target with
    :return: None
    """
    for i in range(spam_limit):
        await target.send(content="GET THE FUCK ON HERE", delete_after=30)

