# TODO: test this version, i havent set up aiogram on my gnu/linux setup and
# im too lazy to do that

# ----------------------------------------------------------------------------
# modules

# builtin modules
from datetime import datetime, timedelta

import asyncio
import logging
import os

# package modules
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandObject, CommandStart, Command

from dotenv import load_dotenv

# custom modules
import remind

# ----------------------------------------------------------------------------
# constants
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ----------------------------------------------------------------------------
# aiogram setup

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------------------------------------------------------------------
# the remindafter command
# aliases: /ra /remind /remindafter
@dp.message(Command(commands=["ra", "remind", "remindafter"]))
async def cmd_remindafter(message: types.Message, command: CommandObject):
    r = remind.remindafter("/ra", command.args)
    if r[0] < 0:
        await message.answer(r[1])
        return
    newtime = datetime.now() + timedelta(seconds=r[0])
    await message.answer(f"set reminder to {newtime.strftime('%c')}")
    await asyncio.sleep(r[0])
    await message.answer(f"REMINDER - {r[1]}")

# ----------------------------------------------------------------------------
# the remindat command
# aliases: /rt /remindat
@dp.message(Command(commands=["rt", "remindat"]))
async def cmd_remindat(message: types.Message, command: CommandObject):
    r = remind.remindat("/ra", command.args)
    if r[0] < 0:
        await message.answer(r[1])
        return
    newtime = datetime.now() + timedelta(seconds=r[0])
    await message.answer(f"set reminder to {newtime.strftime('%c')}")
    await asyncio.sleep(r[0])
    await message.answer(f"REMINDER - {r[1]}")

# ----------------------------------------------------------------------------
# main function
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
