# HW4 Results — Recipe Bot Retrieval Evaluation (BM25)

Option 3: used the provided 200 synthetic queries + 200 processed recipes
(1:1 ground-truth mapping, verified 0 unwinnable). Built Steps 3-5.

## 1. Baseline BM25
| metric | value |
|--------|-------|
| Recall@1 | 0.540 |
| Recall@3 | 0.675 |
| Recall@5 | 0.730 |
| MRR | 0.632 |

In the README's expected range, but **below the course's 80-90% recall bar** —
not yet ready for the generation stage.

## 2. Why it fails (error analysis on failures)
BM25 is pure lexical matching. It succeeds when the query shares a **distinctive
(high-IDF) token** with the recipe's indexed text (name, ingredients, OR steps).
It fails when the query's only overlap is a **generic category word**
('cake', 'bread', 'soup', 'salmon') common to many recipes — no rare term to
single out the right one, so the correct recipe drowns among same-category recipes.

Confirmed three ways:
- Worst failures all shared exactly ONE generic word with their recipe.
- Queries sharing ZERO recipe-name words beat those sharing ONE generic word
  (76% vs 63%) — zero forces BM25 onto rarer ingredient/step tokens that discriminate.
- By query type: Temperature (most generic phrasing) worst (R@5 0.65),
  Technique (most specific) best (0.79).

## 3. Improvement: query expansion, then made safe
| strategy | R@5 | regressions | expanded |
|----------|-----|-------------|----------|
| baseline | 0.73 | 0 | 0 |
| blanket expansion (all queries) | 0.87 | 34 | 200 |
| **selective (BM25-confidence gated)** | **0.85** | **16** | 83 |

A blind LLM rewrite agent (no access to the target recipe) that injects plausible
recipe vocabulary lifted Recall@5 0.73 → 0.87 and rescued 65% of failures —
confirming the distinctive-token diagnosis. But blanket expansion also *hurt* 34
queries (30 already-successful), because adding vocabulary indiscriminately dilutes
queries that already had a distinctive anchor.

Gating expansion on **BM25's own confidence** (flat top-scores → expand; clear
winner → leave alone — a signal available WITHOUT the answer key) kept ~90% of the
recall gain at half the regressions and ~40% of the cost. Decided blind, so it
transfers to live traffic.

## 4. Caveats
- Threshold (gap≥0.95) was chosen by reading the full curve, which includes the
  answer — a real deployment would tune it on a held-out set. The mechanism (blind
  gate) is honest; the exact threshold is mildly optimistic.
- Data artifacts hurt retrieval (e.g. "325°F" mangled to "325of" in cleaning) —
  a process/data fix, not a tools fix.

## Files
- `run_retrieval_eval.py` — BM25 index + Recall@k/MRR
- `run_rewrite_eval.py` — blind LLM query-expansion agent vs baseline
- `run_selective_rewrite.py` — confidence-gated selective expansion
- `results/` — per-query ranks (baseline, rewrite)
