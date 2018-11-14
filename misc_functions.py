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