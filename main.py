# ----------------------------------------------------------------------------
# modules
import asyncio
import logging
import os

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandObject, CommandStart, Command

from dotenv import load_dotenv

# ----------------------------------------------------------------------------
# constants
TIME_UNITS = {
    "s": 1,
    "sec": 1,
    "secs": 1,
    "second": 1,
    "seconds": 1,

    "m": 60,
    "min": 60,
    "mins": 60,
    "minute": 60,
    "minutes": 60,

    "h": 3600,
    "hr": 3600,
    "hrs": 3600,
    "hour": 3600,
    "hours": 3600,

    "d": 86400,
    "day": 86400,
    "days": 86400
}

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ----------------------------------------------------------------------------
# aiogram setup
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------------------------------------------------------------------
# remind the user after a specific amount of time.
# aliases for this command: /ra /remind /remindafter
async def remindafter(message: types.Message, command: CommandObject):
    # usage: /remindafter <time> <message>
    # <time> can be in short format ('10s') or long format ('10 sec' or '10 seconds')
    if not command.args:
        await message.answer("usage: /remindafter <time> <message>")
        return
    args = command.args.split()
    if len(args) < 2:
        await message.answer("usage: /remindafter <time> <message>")
        return
    elif len(args) == 2 or (len(args) > 2 and args[1] not in TIME_UNITS):
        if args[0][:-1].isdigit() and args[0][-1] in TIME_UNITS:
            try:
                tm = int(args[0][:-1]) * TIME_UNITS[args[0][-1]]
            except ValueError:
                await message.answer("usage: /remindafter <time> <message>")
                return
            rm = ' '.join(args[1:])
        else:
            await message.answer("usage: /remindafter <time> <message>")
            return
    elif len(args) >= 3:
        if args[0].isdigit():
            try:
                tm = int(args[0]) * TIME_UNITS[args[1]]
            except ValueError:
                await message.answer("usage: /remindafter <time> <message>")
                return
            rm = ' '.join(args[2:])
        else:
            await message.answer("usage: /remindafter <time> <message>")
            return

    newtime = datetime.now() + timedelta(seconds=tm)
    await message.answer(f"set reminder to {newtime.strftime('%c')}")
    await asyncio.sleep(tm)
    await message.answer(f"REMINDER - {rm}")

# ----------------------------------------------------------------------------
# utility function used in remindat, used to convert a time format to an
# amount of seconds from the current time. see the comment in remindat for the
# time format.
def parsetime(args: list) -> list:
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    hour, minute, second = now.hour, now.minute, now.second

    date = args[0].split("/")
    if len(args) > 2:
        rm = args[2]
        time = args[1].split(":")
        try:
            if len(time) == 3:
                hour, minute, second = int(time[0]), int(time[1]), int(time[2])
            elif len(time) == 2:
                minute, second = int(time[0]), int(time[1])
            elif len(time) == 1:
                second = int(time[0])
        except ValueError:
            return []
    else:
        rm = args[1]

    try:
        if len(date) == 3:
            year, month, day = int(date[0]), int(date[1]), int(date[2])
        elif len(date) == 2:
            month, day = int(date[0]), int(date[1])
        elif len(date) == 1:
            day = int(date[0])
    except ValueError:
        return []

    newtime = datetime(year, month, day, hour, minute, second)
    currtime = datetime.now()
    timedelta = newtime - currtime;
    diff = (timedelta.days * 24 * 3600) + timedelta.seconds
    if diff < 0:
        return []
    return [diff, rm]

# ----------------------------------------------------------------------------
# remind the user at a specific time.
# aliases for this command: /rt /remindat
async def remindat(message: types.Message, command: CommandObject):
    # usage: /remindat <time> <message>
    # <time> has to be in the following format:
    # [year]/[month]/[day] [hour]:[minute]:[second]
    # if less than 6 arguments are passed to <time>, it is assumed that the
    # lower ones are passed and the higher ones default to the current
    # date/time (this is separate for the date and the time),
    # e.g '12:00:00' will remind you at 12 PM of the current day, if that
    # isn't in the past. '08/15 18:30:00' will remind you
    # at 6:30 PM on August 15 of this year, '08/15' will remind you on
    # August 15 at the same time as right now.
    if not command.args:
        await message.answer("usage: /remindat <time> <message>")
        return
    args = command.args.split()
    if len(args) < 2:
        await message.answer("usage: /remindat <time> <message>")
        return
    results = parsetime(args)
    if not results:
        await message.answer("usage: /remindat <time> <message>")
        return
    tm = results[0]
    rm = results[1]
    newtime = datetime.now() + timedelta(seconds=tm)
    await message.answer(f"set reminder to {newtime.strftime('%c')}")
    await asyncio.sleep(tm)
    await message.answer(f"REMINDER - {rm}")

# ----------------------------------------------------------------------------
# aliases for remindafter.
@dp.message(Command("ra"))
async def handle_ra(message: types.Message, command: CommandObject):
    await remindafter(message, command)

@dp.message(Command("remind"))
async def handle_remind(message: types.Message, command: CommandObject):
    await remindafter(message, command)

@dp.message(Command("remindafter"))
async def handle_remindafter(message: types.Message, command: CommandObject):
    await remindafter(message, command)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())