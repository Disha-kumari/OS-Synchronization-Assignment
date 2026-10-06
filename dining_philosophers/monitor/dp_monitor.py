"""Dining Philosophers (4) with a MONITOR (lock + condition variable).
Usage: python dp_monitor.py [delay_seconds]
A philosopher picks up BOTH forks atomically inside the monitor, or waits.
No hold-and-wait => no deadlock.  Starvation is still theoretically possible
(neighbours could keep eating); fix with a queue/ticket or aging."""
import os, random, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))
from simlib import Recorder, write_html

N = 4
DELAY = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
ROUNDS = 4
rec = Recorder()


class Table:                                   # the monitor
    def __init__(self):
        self.cond = threading.Condition()
        self.owner = [None] * N                # fork ownership

    def pickup(self, i):
        name, l, r = f"P{i}", i, (i + 1) % N
        with self.cond:
            rec.state(name, "hungry")
            while self.owner[l] is not None or self.owner[r] is not None:
                self.cond.wait()               # condition: both forks free
            rec.state(name, "acquiring")
            self.owner[l] = name; rec.fork(l, name)
            self.owner[r] = name; rec.fork(r, name)
            rec.state(name, "eating")

    def putdown(self, i):
        name, l, r = f"P{i}", i, (i + 1) % N
        with self.cond:
            rec.state(name, "releasing")
            for f in (l, r):
                self.owner[f] = None; rec.fork(f, None)
            rec.state(name, "thinking")
            self.cond.notify_all()


table = Table()


def philosopher(i):
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0, 2 * DELAY))   # thinking
        table.pickup(i)
        time.sleep(DELAY)                          # eating
        table.putdown(i)


if __name__ == "__main__":
    ths = [threading.Thread(target=philosopher, args=(i,)) for i in range(N)]
    for t in ths: t.start()
    for t in ths: t.join()
    print("All philosophers finished - no deadlock.")
    out = os.path.join(HERE, "..", "..", "generated_html"); os.makedirs(out, exist_ok=True)
    write_html(os.path.join(out, "dining_philosophers_monitor.html"), "Dining Philosophers x4 (Monitor)", "dp",
               rec.events, [{"name": f"P{i}", "role": "Philosopher"} for i in range(N)], nforks=N,
               notes=["Monitor: Condition(lock), both forks taken atomically"])
