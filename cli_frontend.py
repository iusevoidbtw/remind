# ----------------------------------------------------------------------------
# modules

# builtin modules
from datetime import datetime, timedelta
from threading import Timer
from time import sleep

# custom modules
import remind

# ----------------------------------------------------------------------------
# helper function that other threads execute.
def do_remind(msg: str):
    print(f"REMINDER - {msg}")

# ----------------------------------------------------------------------------
# the remindafter command
# aliases: /ra /remind /remindafter
def cmd_remindafter(name: str, query: str):
    r = remind.remindafter(name, query)
    if r[0] < 0:
        print(r[1])
        return
    newtime = datetime.now() + timedelta(seconds=r[0])
    print(f"set reminder to {newtime.strftime('%c')}")
    t = Timer(r[0], do_remind, args=[r[1]])
    t.start()

# ----------------------------------------------------------------------------
# the remindat command
# aliases: /rt /remindat
def cmd_remindat(name: str, query: str):
    r = remind.remindat(name, query)
    if r[0] < 0:
        print(r[1])
        return
    newtime = datetime.now() + timedelta(seconds=r[0])
    print(f"set reminder to {newtime.strftime('%c')}")
    t = Timer(r[0], do_remind, args=[r[1]])
    t.start()

# ----------------------------------------------------------------------------
# the main function
def main():
    try:
        while True:
            cmdstr = input("enter your command:\n")
            cmd = cmdstr.split(maxsplit=1)
            if len(cmd) == 0:
                continue
            elif cmd[0] in ["/ra", "/remind", "/remindafter"]:
                cmd_remindafter(cmd[0], cmd[1])
            elif cmd[0] in ["/rt", "/remindat"]:
                cmd_remindat(cmd[0], cmd[1])
            else:
                print("error: unknown command")
    except (EOFError, KeyboardInterrupt):
        return

if __name__ == "__main__":
    main()
