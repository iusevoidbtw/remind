# ----------------------------------------------------------------------------
# modules
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------
# constants
SECONDS = ["s", "sec", "secs", "second", "seconds"]
MINUTES = ["m", "min", "mins", "minute", "minutes"]
HOURS   = ["h", "hr",  "hrs",  "hour",   "hours"]
DAYS    = ["d", "day", "days"]
WEEKS   = ["w", "wk",  "wks",  "week",   "weeks"]

TIME_UNITS = [
        "s", "sec", "secs", "second", "seconds",
        "m", "min", "mins", "minute", "minutes",
        "h", "hr",  "hrs",  "hour",   "hours",
        "d", "day", "days",
        "w", "wk",  "wks",  "week",   "weeks"
]

# ----------------------------------------------------------------------------
# helper function for adding time to a datetime
def addtime(time: datetime, amount: int, unit: str) -> datetime:
    t = time
    if unit in SECONDS:
        t += timedelta(seconds=amount)
    elif unit in MINUTES:
        t += timedelta(minutes=amount)
    elif unit in HOURS:
        t += timedelta(hours=amount)
    elif unit in DAYS:
        t += timedelta(days=amount)
    elif unit in WEEKS:
        t += timedelta(weeks=amount)
    return t

# ----------------------------------------------------------------------------
# helper function for adding time to an interval, used by remindevery
def addinterval(interval: list, amount: int, unit: str) -> list:
    i = interval[:]
    if unit in SECONDS:
        i[4] += amount
    elif unit in MINUTES:
        i[3] += amount
    elif unit in HOURS:
        i[2] += amount
    elif unit in DAYS:
        i[1] += amount
    elif unit in WEEKS:
        i[0] += amount
    return i

# ----------------------------------------------------------------------------
# usage: remindafter <time>
# <time> can be in short format ('10s') or long format ('10 sec' or '10 seconds')
#
# returns a datetime object at which the reminder should fire.
# raises ValueError on error.
def remindafter(query: str) -> datetime:
    if not query:
        raise ValueError("bad query")
    args = query.split()
    now = datetime.now()
    if len(args) < 1:
        raise ValueError("bad query")

    i = 0
    remaining = len(args)

    while remaining > 0:
        if remaining == 1 or (remaining > 1 and args[i + 1] not in TIME_UNITS):
            if args[i][:-1].isdigit() and args[i][-1] in TIME_UNITS:
                now = addtime(now, int(args[i][:-1]), args[i][-1])
                remaining -= 1
                i += 1
            else:
                raise ValueError("invalid time format")
        elif remaining >= 2:
            if args[i].isdigit() and args[i + 1] in TIME_UNITS:
                now = addtime(now, int(args[i]), args[i + 1])
                remaining -= 2
                i += 2
            else:
                raise ValueError("invalid time format")
        else:
            raise ValueError("invalid time format")
    return now

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
# usage: remindat <time>
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
# returns a datetime object at which the reminder should fire.
# raises ValueError on error.
def remindat(query: str) -> datetime:
    if not query:
        raise ValueError("bad query")
    args = query.split()
    if len(args) < 1 or len(args) > 2:
        raise ValueError("bad query")
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
            raise ValueError("invalid time format")

        if len(args) > 1:
            if not seendate and "/" in args[1] and ":" not in args[1]:
                seendate = True
                year, month, day = parsedate(args[1].split("/"))
            elif not seentime and ":" in args[1] and "/" not in args[1]:
                seentime = True
                hour, minute, second = parsetime(args[1].split(":"))
            else:
                raise ValueError("invalid time format")
    except ValueError:
        raise ValueError("invalid time format")

    now = datetime.now()
    if not seendate:
        year, month, day = now.year, now.month, now.day
    if not seentime:
        hour, minute, second = now.hour, now.minute, now.second
    newtime = datetime(year, month, day, hour, minute, second)

    # sanity check
    timedelta = newtime - now;
    diff = (timedelta.days * 24 * 3600) + timedelta.seconds
    if diff < 0:
        raise ValueError("date/time cannot be in the past")

    return newtime

# ----------------------------------------------------------------------------
# usage: remindevery <time>
# similar to remindafter, but reminds at an interval, e.g 'remindevery 10s'
# will remind you every 10 seconds.
#
# returns a list in the format of [weeks, days, hours, minutes, seconds].
# raises ValueError on error.
def remindevery(query: str, cmdname: str = "remindevery") -> list:
    if not query:
        raise ValueError("bad query")
    args = query.split()
    interval = [0, 0, 0, 0, 0]
    if len(args) < 1:
        raise ValueError("bad query")

    i = 0
    remaining = len(args)

    while remaining > 0:
        if remaining == 1 or (remaining > 1 and args[i + 1] not in TIME_UNITS):
            if args[i][:-1].isdigit() and args[i][-1] in TIME_UNITS:
                interval = addinterval(interval, int(args[i][:-1]), args[i][-1])
                remaining -= 1
                i += 1
            else:
                raise ValueError("invalid time format")
        elif remaining >= 2:
            if args[i].isdigit() and args[i + 1] in TIME_UNITS:
                interval = addinterval(interval, int(args[i + 1]), args[i + 1])
                now = addtime(now, int(args[i]), args[i + 1])
                remaining -= 2
                i += 2
            else:
                raise ValueError("invalid time format")
        else:
            raise ValueError("invalid time format")
    return interval
