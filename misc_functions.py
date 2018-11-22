import random
import codecs
import discord

def get_random_donger():
    lines = codecs.open('dongers.txt', encoding='utf-8').read().splitlines()
    myline =random.choice(lines)
    return myline

def user_info_embed(member : discord.Member):
    name = member.display_name
    rank = member.top_role
    avatar = member.avatar_url
    joined = str(member.joined_at).split(' ')[0]
    status = member.status

    embed = discord.Embed(  title = name, 
                            description = rank.name)
    
    embed.set_image(url = avatar)
    embed.add_field(name = 'Date Joined', value = joined)
    embed.add_field(name = 'Current Status', value = status, inline = False)

    return embed

def russian_roulette(ctx):
    try:
        channel = ctx.message.author.voice.channel
    
    except:
        response = 'You need to be in a voice channel with at least 2 people to do this...'
        return response
    
    members = channel.members
    
    if len(members) > 1:
        r = random.randint(0,5)
        not_shot = 1
        while not_shot:
            for member in members:
                if random.randint(0,5) == r:
                    not_shot = 0
                    name = member.display_name
                    response = "{}: BOOOOOOOOOOOOOOM, HEADSHOT!".format(name)
                    break

    else:
        response = 'You need to be in a voice channel with at least 2 people to do this...'
        return response

    return response

