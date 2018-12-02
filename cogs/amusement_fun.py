import discord
import random
import codecs
import discord


def get_random_donger():
    lines = codecs.open('dongers.txt', encoding='utf-8').read().splitlines()
    myline =random.choice(lines)
    return myline

def russian_roulette(name, death_vals, no_rem, count):

    if count in death_vals:
        response = "BOOOOM HEADSHOT, {} got pwned".format(name)
        hit = 1
    
    else:
        response = "CLICK, {} gets to live another round".format(name)
        hit = 0

    return response, hit