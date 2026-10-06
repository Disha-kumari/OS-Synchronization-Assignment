"""Readers-Writers with a MONITOR (lock + condition variable) - writer preference.
Usage: python rw_monitor.py [readers] [writers] [delay_seconds]
Monitor = class whose methods all run while holding one lock (Condition).
Readers wait while a writer is active OR waiting, so writers cannot starve."""
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


class RWMonitor:
    def __init__(self):
        self.cond = threading.Condition()      # monitor lock + condition variable
        self.readers = 0
        self.writing = False
        self.waiting_writers = 0

    def start_read(self, name):
        with self.cond:                        # enter monitor
            rec.state(name, "waiting")
            while self.writing or self.waiting_writers > 0:
                self.cond.wait()               # releases lock while sleeping
            self.readers += 1
            rec.state(name, "reading", f"value={shared['value']}")

    def end_read(self, name):
        with self.cond:
            self.readers -= 1
            rec.state(name, "idle")
            if self.readers == 0:
                self.cond.notify_all()         # wake waiting writers

    def start_write(self, name):
        with self.cond:
            rec.state(name, "waiting")
            self.waiting_writers += 1
            while self.writing or self.readers > 0:
                self.cond.wait()
            self.waiting_writers -= 1
            self.writing = True
            rec.state(name, "writing", f"value {shared['value']}->{shared['value']+1}")

    def end_write(self, name):
        with self.cond:
            self.writing = False
            rec.state(name, "idle")
            self.cond.notify_all()


mon = RWMonitor()


def reader(name):
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0, 2 * DELAY))
        mon.start_read(name)
        time.sleep(DELAY)                      # reading (shared access)
        mon.end_read(name)


def writer(name):
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0, 2 * DELAY))
        mon.start_write(name)
        v = shared["value"]
        time.sleep(DELAY)                      # exclusive access
        shared["value"] = v + 1
        mon.end_write(name)


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
    write_html(os.path.join(out, "readers_writers_monitor.html"), "Readers-Writers (Monitor)", "rw",
               rec.events, actors, notes=["Monitor: Condition(lock) | writer-preference"])
