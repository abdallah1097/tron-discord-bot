import discord
from commands import _mongoFunctions, _embedMessage


async def send_birthday_message(client, guild_id, channel_id):
    guild_id = int(guild_id)
    channel_id = int(channel_id)
    guild = client.get_guild(guild_id)

    role = discord.utils.get(guild.roles, name = _mongoFunctions.get_birthday_role_string(guild_id))

    for member in guild.members:
        if role in member.roles:
            await member.remove_roles(role)

    birthday_mentions = []

    user_documents = _mongoFunctions.get_all_birthdays_today(guild_id)

    for document in user_documents:
        member = discord.utils.get(guild.members, id = document['user_id'])
        if member is None:
            continue
        birthday_mentions.append(member.mention)
        await member.add_roles(role)

    if len(birthday_mentions) != 0:
        await guild.get_channel(channel_id).send(embed = _embedMessage.create("Happy Birthday!", "Happy birthday to:\n" + ' '.join(birthday_mentions), "blue"))
