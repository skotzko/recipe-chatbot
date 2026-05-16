#!/usr/bin/env python3
"""Step 3: turn the seeded tuple combinations into natural-language queries.

Reads query_combinations.csv (produced by generate_query_combinations.py,
seeded random.seed(42)) and renders each tuple into a realistic user
query, using several phrasing templates so the query set has the messy
variety real users produce (terse asks, context-rich asks, constraint-
buried asks). Seeded for reproducibility.

Output: synthetic_queries_expanded.csv with `id,query` columns -- the
exact format scripts/bulk_test.py expects.

Usage (from this dir):
    python generate_synthetic_queries.py
    # then, from repo root:
    uv run python scripts/bulk_test.py --csv homeworks/hw2/my_work/synthetic_queries_expanded.csv
"""

import csv
import random
from pathlib import Path

HERE = Path(__file__).parent
COMBOS = HERE / "query_combinations.csv"
OUT = HERE / "synthetic_queries_expanded.csv"
SEED = 42
# Use every tuple in query_combinations.csv (50). No trimming -- more
# volume for open coding, and each tuple's constraints are all stated.
TARGET = None

# Human-readable fragments per dimension. Keys match dim*_name values
# in query_combinations.csv. Each returns a phrase given the raw value.
def diet(v):       return v                      # "gluten free", "vegan", ...
def dish(v):       return v                      # "main", "dessert", ...
def meal(v):       return v                      # "breakfast", "dinner", ...
def equip(v):
    table = {
        "microwave only": "I only have a microwave",
        "stove only": "I only have a stove (no oven)",
        "stove and oven": "I have a stove and oven",
        "no microwave": "I don't have a microwave",
        "sous vide": "I have a sous vide setup",
        "air fryer": "I have an air fryer",
    }
    return table.get(v, v)
def people(v):     return f"{v} people" if v != "1" else "just me"
def dishes(v):     return f"{v} dishes" if v != "1" else "a single dish"
def ttime(v):
    return {
        "15 min": "in 15 minutes or less",
        "30 min": "in about 30 minutes",
        "45 min": "in 45 minutes max",
        "1 hour": "in around an hour",
        "2 hour": "I've got a couple hours",
        ">2 hours": "I've got all day to cook",
    }.get(v, f"in {v}")

RENDER = {
    "dietary_restriction": diet,
    "dish_type": dish,
    "meal": meal,
    "equipment_available": equip,
    "number_of_people": people,
    "number_of_dishes": dishes,
    "time_available": ttime,
}

# Phrasing templates. Each takes a dict mapping dim_name -> rendered phrase
# (only the 3 dims present in that tuple). Templates are written to
# tolerate whichever 3 dims appear, falling back gracefully.
def build_query(rng, dims):
    """dims: list of (dim_name, rendered_phrase) for the 3 tuple dims.

    EVERY dimension in the tuple is surfaced in the query (so the bot
    actually sees each constraint and 'ignored constraint' coding is
    fair). Phrasing stays casual and varied -- imperfect punctuation is
    intentional: real users type messy input, and robustness to that is
    a legitimate thing to evaluate.
    """
    d = dict(dims)

    def g(*names):
        for n in names:
            if n in d:
                return d[n]
        return None

    diet_p = g("dietary_restriction")
    dish_p = g("dish_type")
    meal_p = g("meal")
    time_p = g("time_available")
    equip_p = g("equipment_available")
    ppl_p = g("number_of_people")
    dishes_p = g("number_of_dishes")

    # The "thing being asked for" must reflect dish AND meal if both are
    # in the tuple, so neither constraint is silently dropped.
    if dish_p and meal_p:
        core = f"{meal_p} {dish_p}"
    else:
        core = dish_p or meal_p or "recipe"

    # Build a list of standalone constraint clauses for whichever of the
    # remaining dims are present. Each present dim contributes exactly
    # one clause -> all 3 tuple dims always appear.
    def clauses():
        c = []
        if time_p:
            c.append(time_p)                       # "in about 30 minutes"
        if equip_p:
            c.append(equip_p.lower())              # "i have an air fryer"
        if ppl_p:
            c.append(f"for {ppl_p}")               # "for 4 people" / "for just me"
        if dishes_p:
            c.append(f"I need {dishes_p}")         # "I need 3 dishes"
        return c

    extra = clauses()
    rng.shuffle(extra)
    diet_clause = f"{diet_p} " if diet_p else ""

    # Several whole-query shapes; each appends ALL extra clauses so no
    # dimension is lost. Variation is in connective style/order.
    tail_join = rng.choice([
        lambda xs: ". " + ". ".join(s.capitalize() for s in xs) + "." if xs else "",
        lambda xs: " — " + ", ".join(xs) + "." if xs else ".",
        lambda xs: ". " + " and ".join(xs) + "." if xs else ".",
    ])

    shapes = [
        f"Give me a {diet_clause}{core} recipe{tail_join(extra)}",
        f"I need a {diet_clause}{core}{tail_join(extra)}",
        f"Help me make a {diet_clause}{core}{tail_join(extra)}",
        f"What's a good {diet_clause}{core}?{(' ' + ' '.join(s.capitalize()+'.' for s in extra)) if extra else ''}",
        f"Looking for a {diet_clause}{core}{tail_join(extra)}",
    ]
    q = rng.choice(shapes)

    # tidy obvious artifacts but deliberately leave casual tone intact
    q = " ".join(q.split())
    q = (q.replace(" .", ".").replace("..", ".")
           .replace(" ?", "?").replace("?.", "?").replace(".,", ",")
           .replace(". .", ".").replace("  ", " "))
    return q[0].upper() + q[1:] if q else q


def main():
    rng = random.Random(SEED)
    rows = []
    with COMBOS.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            dims = [
                (r["dim1_name"], RENDER[r["dim1_name"]](r["value1"])),
                (r["dim2_name"], RENDER[r["dim2_name"]](r["value2"])),
                (r["dim3_name"], RENDER[r["dim3_name"]](r["value3"])),
            ]
            tuple_str = f'({r["value1"]}, {r["value2"]}, {r["value3"]})'
            rows.append((build_query(rng, dims), tuple_str))

    # de-dup identical rendered queries, keep order. TARGET=None -> use
    # every (unique) tuple-derived query; otherwise trim to TARGET.
    seen, picked = set(), []
    for q, t in rows:
        if q not in seen:
            seen.add(q)
            picked.append((q, t))
        if TARGET is not None and len(picked) >= TARGET:
            break

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "query"])
        for i, (q, _t) in enumerate(picked, 1):
            w.writerow([i, q])

    print(f"Read {len(rows)} tuples from {COMBOS.name}")
    print(f"Wrote {len(picked)} unique queries -> {OUT.name}")
    print("\nSample (first 8):")
    for i, (q, t) in enumerate(picked[:8], 1):
        print(f"  {i}. {q}   {t}")
    print("\nNext: from repo root run")
    print(f"  uv run python scripts/bulk_test.py --csv {OUT.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()
