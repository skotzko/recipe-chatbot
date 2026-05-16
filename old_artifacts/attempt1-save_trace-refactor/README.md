# Archived: `save_trace` refactor from `attempt1`

These are **frozen copies** of my original files from the pre-redesign `attempt1`
branch. They are NOT wired into the live backend. The live `backend/` and
`scripts/` on this branch use the **course's current code** unchanged.

## Why this is archived (not merged)

My `attempt1` work added a `save_trace()` helper to `backend/utils.py` and called
it from both `backend/main.py` (chat endpoint) and `scripts/bulk_test.py`, so the
bulk script would persist conversation traces to `annotation/traces/*.json` the
same way the manual chat path did.

The course later **independently solved the same problem differently**:

- `scripts/bulk_test.py` was rewritten (`read_queries` / `process_query` /
  `write_results`) to emit JSON to `results/results_<ts>.json`.
- HW2 now ships `homeworks/hw2/reference_files/query_response.jsonl` (250
  pre-generated query/response pairs) + a `viewer.html`, so capturing traces
  from the bulk script is no longer required to do the homework.

So porting `save_trace` forward would reintroduce a mechanism the new workflow
doesn't need, and conflict with the rewritten `bulk_test.py`. Archived instead of
discarded so it's recoverable.

## Files

| File | Original location | Notes |
|---|---|---|
| `utils.py` | `backend/utils.py` | Inline `SYSTEM_PROMPT` constant + `save_trace()`. (Prompt itself is preserved separately at `homeworks/hw1/my_work/system_prompt.md`.) |
| `main.py` | `backend/main.py` | Chat endpoint calling `save_trace(...)` instead of inline json.dump |
| `bulk_test.py` | `scripts/bulk_test.py` | Old sync `process_query_sync` calling `save_trace` |
| `save_trace_snippet.py` | — | Just the `save_trace()` function, extracted for easy reuse |

## If I ever want trace-capture in the new bulk script

The new `scripts/bulk_test.py` already writes structured JSON results. If I want
per-trace files too, the minimal path is:

1. Copy `save_trace()` from `save_trace_snippet.py` into the current
   `backend/utils.py`.
2. In the current `scripts/bulk_test.py` `process_query()`, call
   `save_trace([{ "role": "user", "content": query }], updated_history)` before
   returning.

Don't bulk-copy these archived files over the current ones — the surrounding code
has diverged significantly.
