# ----------------------------------------------------------------------------
# modules

# builtin modules
from datetime import datetime, timedelta

# package modules
from apscheduler.schedulers.background import BackgroundScheduler

# custom modules
import remind

# ----------------------------------------------------------------------------
# global variables
scheduler = BackgroundScheduler()
reminders = []
job_ids = []

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
def do_remind(reminder_msg: str, job_id: int):
    print(f"REMINDER - {reminder_msg}")
    if job_id >= 0:
        remove_job_by_id(job_id)

# ----------------------------------------------------------------------------
# the list command, used to list all active reminders
# aliases: /l /ls /list
def cmd_list():
    if len(reminders) == 0:
        print("you don't have any active reminders right now.")
    else:
        for rem in reminders:
            print(f"reminder with ID {rem['job_id']} -- will go off {rem['timestr']}, type: {rem['type']}")

# ----------------------------------------------------------------------------
# the remove command, used to remove an active reminder
# aliases: /r /rm /remove
def cmd_remove(cmdname: str, query: str):
    if not query:
        print(f"usage: {cmdname} <reminder ID>")
        return
    if not query.isdigit():
        print("error: invalid reminder ID")
        return
    remove_job_by_id(int(query))

# ----------------------------------------------------------------------------
# the remindafter command
# aliases: /ra /remind /remindafter
def cmd_remindafter(cmdname: str, query: str):
    try:
        reminder_time = remind.remindafter(cmdname, query)
    except ValueError as e:
        print(e)
        return
    reminder_msg = input("enter the reminder message: ")
    timestr = reminder_time.strftime("%c")
    print(f"set reminder to {timestr}")
    job_id = get_job_id()
    reminders.append({"job": scheduler.add_job(do_remind, "date", args=[reminder_msg, job_id], run_date=reminder_time),
                      "job_id": job_id,
                      "type": "one-time",
                      "timestr": f"at {timestr}"})

# ----------------------------------------------------------------------------
# the remindat command
# aliases: /rt /remindat
def cmd_remindat(cmdname: str, query: str):
    try:
        reminder_time = remind.remindat(cmdname, query)
    except ValueError as e:
        print(e)
        return
    reminder_msg = input("enter the reminder message: ")
    timestr = reminder_time.strftime("%c")
    print(f"set reminder to {timestr}")
    rnum = len(reminders)
    job_id = get_job_id()
    reminders.append({"job": scheduler.add_job(do_remind, "date", args=[reminder_msg, job_id], run_date=reminder_time),
                      "job_id": job_id,
                      "type": "one-time",
                      "timestr": f"at {timestr}"})

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

def cmd_remindevery(cmdname: str, query: str):
    try:
        iv = remind.remindevery(cmdname, query)
    except ValueError as e:
        print(e)
        return
    if not all(v == 0 for v in iv):
        reminder_msg = input("enter the reminder message: ")
        ivstr = intervalstr(iv)
        print(f"set reminder for every {ivstr}")
        job_id = get_job_id()
        reminders.append({"job": scheduler.add_job(do_remind, "interval", args=[reminder_msg, -1], weeks=iv[0], days=iv[1], hours=iv[2], minutes=iv[3], seconds=iv[4]),
                          "job_id": job_id,
                          "type": "repeating",
                          "timestr": f"every {ivstr}"})

# ----------------------------------------------------------------------------
# the main function
def main():
    scheduler.start()
    try:
        while True:
            cmdstr = input("enter your command: ")
            cmd = cmdstr.split(maxsplit=1)
            if len(cmd) == 0:
                continue
            elif cmd[0] in ["/l", "/ls", "/list"]:
                cmd_list()
            elif cmd[0] in ["/r", "/rm", "/remove"]:
                cmd_remove(cmd[0], cmd[1])
            elif cmd[0] in ["/ra", "/remind", "/remindafter"]:
                cmd_remindafter(cmd[0], cmd[1])
            elif cmd[0] in ["/rt", "/remindat"]:
                cmd_remindat(cmd[0], cmd[1])
            elif cmd[0] in ["/re", "/remindevery"]:
                cmd_remindevery(cmd[0], cmd[1])
            else:
                print("error: unknown command")
    except (EOFError, KeyboardInterrupt):
        return

if __name__ == "__main__":
    main()
