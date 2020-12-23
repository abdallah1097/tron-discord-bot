import discord
from datetime import date, datetime, timedelta
from commands import _birthdayMessage, _mongoFunctions, _setBotStatus, _dueDateMessage, _embedMessage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


async def send_morning_announcement(client, guild_id, channel_id):
    await client.get_guild(guild_id).get_channel(channel_id).purge(limit = None, check = lambda msg: not msg.pinned)
    role = discord.utils.get(client.get_guild(guild_id).roles, name = _mongoFunctions.get_settings(guild_id)['announcement_role'])
    await client.get_guild(guild_id).get_channel(channel_id).send(role.mention, embed = _embedMessage.create("Good Morning!", _mongoFunctions.random_quote(guild_id,
                                                                                                                                                           _mongoFunctions.get_settings(
                                                                                                                                                               guild_id)[
                                                                                                                                                               'announcement_quoted_person']),
                                                                                                             "blue"))
    await _birthdayMessage.send_birthday_message(client, guild_id, channel_id)
    _mongoFunctions.set_last_announcement_time(guild_id, datetime.now())


async def check_if_morning_announcement_occurred_today(client, guild_id, channel_id):
    last_announcement_time = _mongoFunctions.get_settings(guild_id)['last_announcement_time']
    if last_announcement_time is None or (last_announcement_time.date() != date.today()):
        await send_morning_announcement(client, guild_id, channel_id)


async def schedule_announcement(client):
    guild_list = _mongoFunctions.get_guilds_information()
    await _setBotStatus.set_random_bot_status(client)

    for guild in guild_list:
        global guild_id, channel_id
        for key, value in guild.items():
            if key == 'guild_id':
                guild_id = value
            if key == 'channel_id':
                channel_id = value

        time = _mongoFunctions.get_settings(guild_id)['announcement_time'].split(':')
        time_object = datetime.today()
        time_object = time_object.replace(hour = int(time[0]), minute = int(time[1]))

        scheduler.add_job(send_morning_announcement, 'cron', hour = time_object.hour, minute = time_object.minute, second = 1, args = [client, guild_id, channel_id])
        time_object += timedelta(minutes = 5)
        scheduler.add_job(check_if_morning_announcement_occurred_today, 'cron', hour = time_object.hour, minute = time_object.minute, second = 1,
                          args = [client, guild_id, channel_id])

    scheduler.add_job(_dueDateMessage.edit_due_date_message, 'interval', minutes = 1, args = [client])
    scheduler.start()
