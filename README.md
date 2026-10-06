# OS Synchronization Assignment - Readers-Writers & Dining Philosophers

**Student name:** Disha Kumari
**Registration / USN:** NNM24IS074
**Course:** Operating Systems

## 1. What this project contains
Four synchronization programs. Each one runs real threads, records every state change, and **generates an HTML simulation from that recorded trace**.

| # | Problem | Technique | File |
|---|---------|-----------|------|
| 1 | Readers-Writers | Semaphores (`mutex`, `rw_lock`), readers-preference | `readers_writers/semaphore/rw_semaphore.py` |
| 2 | Readers-Writers | Monitor (lock + condition variable), writer-preference | `readers_writers/monitor/rw_monitor.py` |
| 3 | Dining Philosophers (4) | Semaphores (4 fork semaphores + `room=3`) | `dining_philosophers/semaphore/dp_semaphore.py` |
| 4 | Dining Philosophers (4) | Monitor (both forks taken atomically) | `dining_philosophers/monitor/dp_monitor.py` |

Shared helper: `common/simlib.py` (event `Recorder` + HTML generator).

## 2. Language and requirements
- Python 3.8 or newer. **No external libraries** (only the standard library: `threading`, `time`, `json`, `random`).
- Any modern web browser to view the HTML.

## 3. Build / compile
Python needs no compilation.

## 4. How to run (this also generates the HTML)
From the project root:
```
python readers_writers/semaphore/rw_semaphore.py
python readers_writers/monitor/rw_monitor.py
python dining_philosophers/semaphore/dp_semaphore.py
python dining_philosophers/monitor/dp_monitor.py
```
(Use `python3` on Mac/Linux. `./run_all.sh` runs all four.)

Optional arguments:
- Readers-Writers: `python <file> [readers] [writers] [delay_seconds]`, e.g. `... 5 3 0.2`
- Dining Philosophers: `python <file> [delay_seconds]`, e.g. `... 0.3`

## 5. How to view the simulation
Each run writes an HTML file into `generated_html/`. Double-click it to open it in a browser, then use **Start / Pause / Reset**, the speed selector and the timeline slider. Re-running a program creates a fresh trace and overwrites the file.

## 6. Expected output
```
Final value = 6 (expected 6) -> OK            (Readers-Writers)
All philosophers finished - no deadlock.      (Dining Philosophers)
HTML written -> .../generated_html/<name>.html
```

## 7. Screenshots
See the `screenshots/` folder (terminal output and the four HTML simulations).

## 8. How the HTML is generated
Threads call `rec.state(...)` / `rec.fork(...)` at each state change. `write_html()` embeds that event list as JSON in an HTML page whose JavaScript replays the events. Nothing is hand-scripted.

## 9. Known limitations
- Replay uses a fixed step speed, not exact real-time gaps (real timestamps are shown in the log).
- Python semaphores/conditions are not strictly FIFO, so starvation cannot be fully excluded.
- Semaphore Readers-Writers uses readers-preference, so writers can starve in theory.
- Monitor Dining Philosophers can theoretically starve a philosopher whose neighbours keep eating.

## 10. AI tools used
Claude (Anthropic). Prompt log: [ai_prompts/prompts.md](ai_prompts/prompts.md)

## 11. References and acknowledgements
See [references/references.md](references/references.md)