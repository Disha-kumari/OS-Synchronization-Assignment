"""Readers-Writers with SEMAPHORES (first problem: readers preference).
Usage: python rw_semaphore.py [readers] [writers] [delay_seconds]
Shared resource : shared["value"]      Critical section: code between acquire/release of rw_lock
mutex   (init 1): protects read_count
rw_lock (init 1): writer gets exclusive access; the FIRST reader locks it for all readers, the LAST reader frees it.
Starvation note : a steady stream of readers can starve writers (readers preference)."""
import os, random, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))
from simlib import Recorder, write_html

NUM_READERS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
NUM_WRITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 2
DELAY = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
ROUNDS = 3

rec = Recorder()
shared = {"value": 0}
mutex = threading.Semaphore(1)
rw_lock = threading.Semaphore(1)
read_count = 0


def reader(name):
    global read_count
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0, 2 * DELAY))            # doing other work
        rec.state(name, "waiting")
        mutex.acquire()                                     # wait(mutex)
        read_count += 1
        if read_count == 1:
            rw_lock.acquire()                               # first reader blocks writers
        mutex.release()                                     # signal(mutex)
        rec.state(name, "reading", f"value={shared['value']}")   # ---- critical section (shared read)
        time.sleep(DELAY)
        rec.state(name, "idle")                             # log BEFORE leaving, keeps trace ordered
        mutex.acquire()
        read_count -= 1
        if read_count == 0:
            rw_lock.release()                               # last reader lets writers in
        mutex.release()


def writer(name):
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0, 2 * DELAY))
        rec.state(name, "waiting")
        rw_lock.acquire()                                   # exclusive access
        v = shared["value"]                                 # ---- critical section (read-modify-write)
        rec.state(name, "writing", f"value {v}->{v+1}")
        time.sleep(DELAY)                                   # without the lock this would lose updates
        shared["value"] = v + 1
        rec.state(name, "idle")
        rw_lock.release()


if __name__ == "__main__":
    actors = [{"name": f"R{i+1}", "role": "Reader"} for i in range(NUM_READERS)] + \
             [{"name": f"W{i+1}", "role": "Writer"} for i in range(NUM_WRITERS)]
    ths = [threading.Thread(target=reader, args=(f"R{i+1}",)) for i in range(NUM_READERS)] + \
          [threading.Thread(target=writer, args=(f"W{i+1}",)) for i in range(NUM_WRITERS)]
    for t in ths: t.start()
    for t in ths: t.join()
    expected = NUM_WRITERS * ROUNDS
    print(f"Final value = {shared['value']} (expected {expected}) ->", "OK" if shared["value"] == expected else "RACE!")
    out = os.path.join(HERE, "..", "..", "generated_html"); os.makedirs(out, exist_ok=True)
    write_html(os.path.join(out, "readers_writers_semaphore.html"), "Readers-Writers (Semaphore)", "rw",
               rec.events, actors, notes=["Semaphores: mutex=1, rw_lock=1 | readers-preference"])
