import codecs
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
