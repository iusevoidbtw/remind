# ----------------------------------------------------------------------------
# modules

# builtin modules
from datetime import datetime, timedelta

import asyncio
import logging
import os

# package modules
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandObject, CommandStart, Command

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv

# custom modules
import remind

# ----------------------------------------------------------------------------
# global variables
load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

scheduler = AsyncIOScheduler()
reminders = []
job_ids = []

# TODO: replace these global variables with a FSM
waiting_for_prompt = False
reminder_time = None
reminder_interval = []

# ----------------------------------------------------------------------------
# job management

# get a job id.
def get_job_id() -> int:
    job_id = 0
    while job_id in job_ids:
        job_id += 1
    job_ids.append(job_id)
    return job_id

# remove a job by its job id.
def remove_job_by_id(job_id: int):
    for rem in reminders[:]:
        if rem["job_id"] == job_id:
            if rem["type"] == "repeating":
                rem["job"].remove()
            job_ids.remove(rem["job_id"])
            reminders.remove(rem)

# ----------------------------------------------------------------------------
# print a reminder message - used by scheduled jobs
async def do_remind(message: types.Message, job_id: int):
    await message.answer(f"REMINDER - {message.text}")
    if job_id >= 0:
        remove_job_by_id(job_id)

# ----------------------------------------------------------------------------
# the list command, used to list all active reminders
# aliases: /l /ls /list
@dp.message(Command(commands=["l", "ls", "list"]))
async def cmd_list(message: types.Message, command: CommandObject):
    if len(reminders) == 0:
        await message.answer("you don't have any active reminders right now.")
    else:
        answer = ""
        for rem in reminders:
            answer += f"reminder with ID {rem['job_id']} -- will go off {rem['timestr']}, type: {rem['type']}\n"
        await message.answer(answer[:-1]) # strip unneeded final newline

# ----------------------------------------------------------------------------
# the remove command, used to remove an active reminder
# aliases: /r /rm /remove
@dp.message(Command(commands=["r", "rm", "remove"]))
async def cmd_remove(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer(f"usage: {message.text.split()[0]} <reminder ID>")
        return
    if not command.args.isdigit():
        await message.answer("error: invalid reminder ID")
        return
    remove_job_by_id(int(command.args))

# ----------------------------------------------------------------------------
# the remindafter command
# aliases: /ra /remind /remindafter
@dp.message(Command(commands=["ra", "remind", "remindafter"]))
async def cmd_remindafter(message: types.Message, command: CommandObject):
    global reminder_type, waiting_for_prompt
    try:
        global reminder_time
        reminder_time = remind.remindafter(command.args, message.text.split()[0])
    except ValueError as e:
        await message.answer(e)
        return
    print("h")
    await message.answer("enter the reminder message: ")
    reminder_type = "one-time"
    waiting_for_prompt = True

# ----------------------------------------------------------------------------
# the remindat command
# aliases: /rt /remindat
@dp.message(Command(commands=["rt", "remindat"]))
async def cmd_remindat(message: types.Message, command: CommandObject):
    global reminder_type, waiting_for_prompt
    try:
        global reminder_time
        reminder_time = remind.remindat(command.args, message.text.split()[0])
    except ValueError as e:
        await message.answer(e)
        return
    await message.answer("enter the reminder message: ")
    reminder_type = "one-time"
    waiting_for_prompt = True

# ----------------------------------------------------------------------------
# the remindevery command
# aliases: /re /remindevery

# helper function used by cmd_remindevery -- convert an interval list to a
# string description
def intervalstr(interval: list) -> str:
    s = ""
    if interval[0] > 0:
        s += f"{interval[0]} weeks, "
    if interval[1] > 0:
        s += f"{interval[1]} days, "
    if interval[2] > 0:
        s += f"{interval[2]} hours, "
    if interval[3] > 0:
        s += f"{interval[3]} minutes, "
    if interval[4] > 0:
        s += f"{interval[4]} seconds, "
    return s[:-2]

@dp.message(Command(commands=["re", "remindevery"]))
async def cmd_remindevery(message: types.Message, command: CommandObject):
    try:
        iv = remind.remindevery(command.args, message.text.split()[0])
    except ValueError as e:
        await message.answer(e)
        return
    if not all(v == 0 for v in iv):
        global reminder_interval, reminder_type, waiting_for_prompt
        await message.answer("enter the reminder message: ")
        reminder_interval = iv
        reminder_type = "repeating"
        waiting_for_prompt = True

# ----------------------------------------------------------------------------
# if we're waiting for a prompt, this function will respond to a message
# and set a reminder with the message that we got
@dp.message(F.text)
async def reminder_prompt(message: types.Message):
    global waiting_for_prompt
    if waiting_for_prompt:
        if reminder_type == "one-time":
            waiting_for_prompt = False
            timestr = reminder_time.strftime("%c")
            await message.answer(f"set reminder to {timestr}")
            job_id = get_job_id()
            reminders.append({"job": scheduler.add_job(do_remind, "date", args=[message, job_id], run_date=reminder_time),
                              "job_id": job_id,
                              "type": "one-time",
                              "timestr": f"at {timestr}"})
        elif reminder_type == "repeating":
            iv = reminder_interval
            ivstr = intervalstr(iv)
            await message.answer(f"set reminder for every {ivstr}")
            job_id = get_job_id()
            reminders.append({"job": scheduler.add_job(do_remind, "interval", args=[message, -1], weeks=iv[0], days=iv[1], hours=iv[2], minutes=iv[3], seconds=iv[4]),
                              "job_id": job_id,
                              "type": "repeating",
                              "timestr": f"every {ivstr}"})

# ----------------------------------------------------------------------------
# the main function
async def main():
    scheduler.start()
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
