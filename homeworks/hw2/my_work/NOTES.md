# HW2 — My Work (ported from attempt1)

These are my in-progress HW2 notes from before resuming the course. The course
**rewrote the HW2 assignment** since I forked, so the official flow now lives in
`../README.md` and ships `../reference_files/` (250-pair `query_response.jsonl`,
`viewer.html`, `failure_mode_taxonomy.md` template). My original work is preserved
here so nothing is lost.

> Status when I paused: finished Part 1 (dimensions → tuples → synthetic queries).
> Part 2 (run bot, open coding, axial coding, taxonomy) **not started** —
> `error_analysis.csv` is just a header row.

---

## Part 1 — Synthetic Query Generation (DONE)

### Step 1: Key Dimensions

- `dietary_restriction`: gluten free, dairy free, keto, low carb, vegetarian, vegan, pescatarian
- `dish_type`: appetizer, main, dessert, side, salad
- `time_available`: 15 min, 30 min, 45 min, 1 hour, 2 hour, >2 hours
- `number_of_people`: 1, 2, 3, 4, 6, 8
- `number_of_dishes`: 1, 2, 3, 4, 5
- `meal`: breakfast, lunch, dinner, snack
- `equipment_available`: microwave only, stove only, stove and oven, no microwave, sous vide, air fryer

### Step 2: Unique Tuple Combos

Two routes I used:

1. **LLM prompt** (the prompt I wrote is below) → ~50 hand-collected 3-tuples.
2. **Script**: `generate_query_combinations.py` (seeded `random.seed(42)` for
   reproducibility) → `query_combinations.csv` (50 rows, with dimension names).

LLM prompt I used:

> Taking the below dimensions + example values, generate ~50 unique 3-tuple combinations of the values.
>
> Output 3-tuples where each tuple is only values (don't include dimension names in the tuple). Here are the dimensions and values:
>
> - `dietary_restriction`: gluten free, dairy free, keto, low carb, vegetarian, vegan, pescatarian
> - `dish_type`: appetizer, main, dessert, side, salad
> - `time_available`: 15 min, 30 min, 45 min, 1 hour, 2 hour, >2 hours
> - `number_of_people`: 1, 2, 3, 4, 6, 8
> - `number_of_dishes`: 1, 2, 3, 4, 5
> - `meal`: breakfast, lunch, dinner, snack
> - `equipment_available`: microwave only, stove only, stove and oven, no microwave, sous vide, air fryer
>
> Select a unique combination of 3 dimensions from the list of 8 dimensions (e.g. dish_type, meal, number_of_people), then select a value from each of those dimensions to make a unique 3-tuple, with each position in the tuple representing a value selected from the set for each dimension selected.
>
> Each 3-tuple of values should be unique within the overall list of tuples.

### Step 3: Natural-Language User Queries

LLM prompt: *generate realistic user queries a user might input to a recipe
chatbot. Select 5–7 tuples from the sample data, generate one natural-language
query per tuple.* Final 7 queries are in `synthetic_queries.csv`:

1. I need a quick vegan dessert I can make in 30 minutes or less — `(vegan, dessert, 30 min)`
2. What's a good low carb recipe I can make in my air fryer? Need something quick, maybe 30 min — `(low carb, air fryer, 30 min)`
3. Give me a pescatarian main dish recipe that I can make in about an hour — `(pescatarian, main, 1 hour)`
4. I'm hosting a lunch for 8 people and need some good appetizer ideas — `(lunch, appetizer, 8)`
5. Looking for a keto-friendly salad recipe. I have access to stove and oven if I need to roast anything — `(keto, salad, stove and oven)`
6. Need to make dairy free lunch for 8 people. What would you suggest? — `(dairy free, lunch, 8)`
7. Help me with a main dish for 3 people that I can get done in 45 minutes max — `(main, 3, 45 min)`

---

## Part 2 — Error Analysis (NOT STARTED)

Open questions / TODOs I had logged before the course redesign (several are now
**resolved by the redesign** — annotated inline):

- ~~"Am I missing some automated tool for getting traces, or do I run them manually?"~~
  → **Resolved**: the new HW2 ships `reference_files/query_response.jsonl` (250
  pairs) + `viewer.html`. No need to capture traces myself.
- ~~"How do I record full traces? They save automatically to `annotation/traces`
  on manual chat but not from the bulk script. TODO: update bulk script to
  record traces."~~ → **Resolved/obsolete**: course rewrote `scripts/bulk_test.py`
  to write JSON to `results/`, and HW2 no longer depends on me capturing traces.
  My old `save_trace` refactor is archived in `/old_artifacts/` if ever needed.
- "How many traces to code — just 5–7, or 100+?" → still a real question;
  the new README/reference data (250 pairs) implies code a meaningful sample,
  not just 7.

### Next steps (on the NEW structure)

1. Read `../README.md` (rewritten flow) and skim `../reference_files/viewer.html`
   over `query_response.jsonl`.
2. Decide: use my 7 synthetic queries, or the course's 250-pair dataset (likely
   the latter for open coding volume).
3. Open coding → axial coding → fill `../reference_files/failure_mode_taxonomy.md`.
4. Track in a spreadsheet (my empty-header `error_analysis.csv` can be the start,
   but the new README's column scheme supersedes it).

---

## File inventory

| File | What it is |
|---|---|
| `synthetic_queries.csv` | My 7 final Part-1 natural-language queries |
| `query_combinations.csv` | 50 tuples from the generator script |
| `generate_query_combinations.py` | Seeded tuple generator (output path patched to relative) |
| `error_analysis.csv` | Empty analysis sheet (header only — Part 2 not started) |
