# ----------------------------------------------------------------------------
# modules
from datetime import datetime, timedelta

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
    "hours": 3600
}

# ----------------------------------------------------------------------------
# usage: /remindafter <time> <message>
# <time> can be in short format ('10s') or long format ('10 sec' or '10 seconds')
#
# returns the amount of seconds needed to sleep and the reminder message.
# returns [-1, <error message>] on error.
def remindafter(name: str, query: str) -> list:
    if not query:
        return [-1, f"usage: {name} <time> <message>"]
    args = query.split()
    if len(args) < 2:
        return [-1, f"usage: {name} <time> <message>"]
    elif len(args) == 2 or (len(args) > 2 and args[1] not in TIME_UNITS):
        if args[0][:-1].isdigit() and args[0][-1] in TIME_UNITS:
            try:
                tm = int(args[0][:-1]) * TIME_UNITS[args[0][-1]]
            except ValueError:
                return [-1, "error: invalid time format"]
            msg = ' '.join(args[1:])
        else:
            return [-1, "error: invalid time format"]
    elif len(args) >= 3:
        if args[0].isdigit():
            try:
                tm = int(args[0]) * TIME_UNITS[args[1]]
            except ValueError:
                return [-1, "error: invalid time format"]
            msg = ' '.join(args[2:])
        else:
            return [-1, "error: invalid time format"]
    return [tm, msg]

# ----------------------------------------------------------------------------
# helper functions for remindat
def parsedate(date: list) -> list:
    if len(date) == 3:
        return [int(date[0]), int(date[1]), int(date[2])]
    elif len(date) == 2:
        return [int(date[0]), int(date[1])]
    elif len(date) == 1:
        return [int(date[0])]

def parsetime(time: list) -> list:
    if len(time) == 3:
        return [int(time[0]), int(time[1]), int(time[2])]
    elif len(time) == 2:
        return [int(time[0]), int(time[1])]
    elif len(time) == 1:
        return [int(time[0])]

# ----------------------------------------------------------------------------
# usage: /remindat <time> <message>
# <time> has to be in the following format:
# [year]/[month]/[day] [hour]:[minute]:[second]
# or this format:
# [hour]:[minute]:[second] [year]/[month]/[day]
# if less than 6 arguments are passed to <time>, it is assumed that the
# lower ones are passed and the higher ones default to the current
# date/time (this is separate for the date and the time),
# e.g '12:00:00' will remind you at 12 PM of the current day, if that
# isn't in the past. '08/15 18:30:00' will remind you
# at 6:30 PM on August 15 of this year, '08/15' will remind you on
# August 15 at the same time as right now.
#
# returns the amount of seconds needed to sleep and the reminder message.
# returns [-1, <error message>] on error.
def remindat(name: str, query: str) -> list:
    if not query:
        return [-1, f"usage: {name} <time> <message>"]
    args = query.split()
    if len(args) < 2:
        return [-1, f"usage: {name} <time> <message>"]
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    hour, minute, second = now.hour, now.minute, now.second

    try:
        seendate, seentime = False, False
        if "/" in args[0] and ":" not in args[0]:
            seendate = True
            year, month, day = parsedate(args[0].split("/"))
        elif ":" in args[0] and "/" not in args[0]:
            seentime = True
            hour, minute, second = parsetime(args[0].split(":"))
        else:
            return [-1, "error: invalid time format"]

        if len(args) > 2:
            msg = args[2]
            if not seendate and "/" in args[1] and ":" not in args[1]:
                year, month, day = parsedate(args[1].split("/"))
            elif not seentime and ":" in args[1] and "/" not in args[1]:
                hour, minute, second = parsetime(args[1].split(":"))
            else:
                return [-1, "error: invalid time format"]
        else:
            msg = args[1]
    except ValueError:
        return [-1, "error: invalid time format"]

    newtime = datetime(year, month, day, hour, minute, second)
    currtime = datetime.now()
    timedelta = newtime - currtime;
    diff = (timedelta.days * 24 * 3600) + timedelta.seconds
    if diff < 0:
        return [-1, "error: date/time cannot be in the past"]
    return [diff, msg]
