import discord


def user_info_embed(member):
    """Fill empty user embed template with supplied user information

    :param member: string or discord.Member
    :return: discord.Embed object formatted with member specific information
    """
    name = member.display_name
    rank = member.top_role
    avatar = member.avatar_url
    joined = str(member.joined_at).split(" ")[0]
    status = member.status

    embed = discord.Embed(title=name, description=rank.name)

    embed.set_image(url=avatar)
    embed.add_field(name="Date Joined", value=joined, inline=True)
    embed.add_field(name="Current Status", value=status, inline=True)

    return embed
