# HW1 — My Work

Ported from my original `attempt1` branch (pre-course-redesign fork).

## What's here

- **`system_prompt.md`** — My structured system prompt from HW1 Part 1. Originally written as an inline `SYSTEM_PROMPT` string constant in `backend/utils.py` (the old HW1 instructions). The course later moved the prompt into `backend/system_prompt.md` loaded via `read_text()`.

## How to use it for HW1

The current HW1 readme (Part 1) says: *"Replace `backend/system_prompt.md` with a well-crafted system prompt."* This file IS that deliverable. When working HW1:

```bash
cp homeworks/hw1/my_work/system_prompt.md backend/system_prompt.md
```

Then run the bulk test per Part 3.

> `backend/system_prompt.md` is intentionally left as the course's placeholder on this branch so the diff stays clean. Swap it in when you actually do HW1.

## HW1 Part 2 (sample queries)

Already done: my 12 additional diverse queries (ids 4–15) are merged into `data/sample_queries.csv` on this branch, appended after the course's 3 starter rows.
