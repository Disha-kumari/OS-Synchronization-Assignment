# AI Prompt Log

**Student:** Disha Kumari (NNM24IS074)
**AI tool used:** Claude (Anthropic), chat interface

## 1. Initial prompt
I uploaded the assignment PDF and told Claude that  how to start. 
I asked for a structured plan, the requirements, and working code for
the four synchronization problems (Readers-Writers and Dining Philosophers,
each with semaphores and monitors) with program-generated HTML simulations.

## 2. Important follow-up prompts
1. Asked for step-by-step instructions, because the assignment felt too big
   to start.
2. Asked how to run the code in VS Code and what output to expect.
3. Asked Claude to explain all four programs in simple words, and to list
   modifications my teacher might ask for in the viva.
4. Asked for the GitHub upload steps, README, prompt log, references and a
   report draft.
5. Asked Claude to check my complete project and give a checklist of fixes.
   This found that the `common/` folder was missing from my copy, so I added it.

## 3. What I changed or did myself
- Added my name and USN to the README and the report.
- Ran the programs on my computer and generated the HTML simulations.
- Took all terminal and HTML screenshots from my own runs.

## 4. Reflection: limitations and improvements I found
- **Replay speed:** The HTML replay moves at a fixed speed instead of using
  the real time gaps between events. An improvement would be to scale the
  delays using the recorded timestamps.
- **Fairness:** Python semaphores and condition variables are not strictly
  FIFO, so starvation cannot be completely ruled out.
- **Readers-Writers:** The semaphore solution favours readers, so writers can
  starve in theory. The monitor solution fixes this with writer preference.