from datetime import datetime, timedelta
from commands import _birthdayMessage, _mongoFunctions, _dueDateMessage, _morningAnnouncement, _util
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


async def schedule_jobs(client):
    guild_list = _mongoFunctions.get_guilds_information()

    for guild in guild_list:
        guild_id = guild['guild_id']
        channel_id = guild['channel_id']

        guild_timezone = guild['timezone']

        scheduler.add_job(_util.purge_messages_in_channel, 'cron', hour = 23, minute = 59, second = 0, timezone = guild_timezone, args = [client, guild_id, channel_id])

        birthday_time = _mongoFunctions.get_birthday_time(guild_id).split(':')

        scheduler.add_job(_birthdayMessage.send_birthday_message, 'cron', hour = int(birthday_time[0]), minute = int(birthday_time[1]), second = 1, timezone = guild_timezone,
                          args = [client, guild_id, channel_id])

        announcement_time = _mongoFunctions.get_announcement_time(guild_id).split(':')
        announcement_time_object = datetime.today()
        announcement_time_object = announcement_time_object.replace(hour = int(announcement_time[0]), minute = int(announcement_time[1]))

        scheduler.add_job(_morningAnnouncement.send_morning_announcement, 'cron', hour = announcement_time_object.hour, minute = announcement_time_object.minute, second = 1,
                          timezone = guild_timezone, args = [client, guild_id, channel_id])
        announcement_time_object += timedelta(minutes = 5)
        scheduler.add_job(_morningAnnouncement.check_if_morning_announcement_occurred_today, 'cron', hour = announcement_time_object.hour, minute = announcement_time_object.minute,
                          second = 1, timezone = guild_timezone, args = [client, guild_id, channel_id])

    scheduler.add_job(_dueDateMessage.edit_due_date_message, 'interval', minutes = 1, args = [client])
    scheduler.start()
