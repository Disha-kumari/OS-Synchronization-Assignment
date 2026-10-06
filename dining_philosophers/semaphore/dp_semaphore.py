"""Dining Philosophers (4) with SEMAPHORES.
Usage: python dp_semaphore.py [delay_seconds]
forks[i] (init 1): one semaphore per fork. Fork i is between P(i) and P(i+1).
room     (init 3): at most N-1 philosophers may try to pick up forks at once.
Deadlock prevention: circular wait needs all 4 holding a fork; room=3 makes that impossible.
Starvation note: Python semaphores give no strict FIFO guarantee, so starvation is unlikely but not formally excluded."""
import os, random, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))
from simlib import Recorder, write_html

N = 4
DELAY = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
ROUNDS = 4
rec = Recorder()
forks = [threading.Semaphore(1) for _ in range(N)]
room = threading.Semaphore(N - 1)


def philosopher(i):
    name, left, right = f"P{i}", i, (i + 1) % N
    for _ in range(ROUNDS):
        rec.state(name, "thinking")
        time.sleep(random.uniform(0, 2 * DELAY))
        rec.state(name, "hungry")
        room.acquire()                                  # enter the "room" (max 3)
        rec.state(name, "acquiring")
        forks[left].acquire();  rec.fork(left, name)
        time.sleep(random.uniform(0, DELAY))            # widens the window where deadlock WOULD happen
        forks[right].acquire(); rec.fork(right, name)
        rec.state(name, "eating")                       # ---- critical section (two forks held)
        time.sleep(DELAY)
        rec.state(name, "releasing")
        rec.fork(left, None);  forks[left].release()    # log first, then release
        rec.fork(right, None); forks[right].release()
        room.release()
    rec.state(name, "thinking")


if __name__ == "__main__":
    ths = [threading.Thread(target=philosopher, args=(i,)) for i in range(N)]
    for t in ths: t.start()
    for t in ths: t.join()
    print("All philosophers finished - no deadlock.")
    out = os.path.join(HERE, "..", "..", "generated_html"); os.makedirs(out, exist_ok=True)
    write_html(os.path.join(out, "dining_philosophers_semaphore.html"), "Dining Philosophers x4 (Semaphore)", "dp",
               rec.events, [{"name": f"P{i}", "role": "Philosopher"} for i in range(N)], nforks=N,
               notes=["Semaphores: fork[0..3]=1 each, room=3 (deadlock avoidance)"])
