import discord


def user_info_embed(member: discord.Member) -> discord.Embed:
    """Fill empty user embed template with supplied user information

    :param member: string or discord.Member
    :return: discord.Embed object formatted with member specific information
    """
    name = member.display_name
    rank = member.top_role
    embed = discord.Embed(title=name, description=rank.name)
    if member.avatar:
        avatar = member.avatar.url
        embed.set_image(url=avatar)
    joined = str(member.joined_at).split(" ")[0]
    status = member.status

    embed.add_field(name="Date Joined", value=joined, inline=True)
    embed.add_field(name="Current Status", value=status, inline=True)

    return embed
