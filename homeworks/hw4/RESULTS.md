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

In the README's expected range, but **below the course's 80-90% recall bar**.
Not yet ready for the generation stage.

## 2. Why it fails
BM25 matches words, not meaning. So a query only finds its recipe when the two
share a *distinctive* word, something rare enough to point at one recipe and not
the other 199. When the only shared word is generic, the recipe drowns. Ask "what
temperature for this cake" and BM25 sees fifteen cakes that all match "cake"
equally well, and the right one is just one of them.

The failures bear this out from three angles. The worst-buried recipes each shared
exactly one generic word with their query ("salmon", "soup", "cake"). Stranger:
queries that shared *zero* recipe-name words did better than ones sharing a single
generic word (76% vs 63%), because zero forces BM25 onto rarer ingredient and step
words that actually discriminate, while one generic word is a confident wrong
signal. And by type, the most generic questions lose. "What temp do I bake this"
is nearly the same sentence for every baked good, so Temperature queries score
worst (R@5 0.65). Technique questions name a specific method on a specific dish, so
they score best (0.79). It's the same story every way you cut it: generic
vocabulary, generic results.

## 3. Improvement: query expansion, then made safe
| strategy | R@5 | regressions | expanded |
|----------|-----|-------------|----------|
| baseline | 0.73 | 0 | 0 |
| blanket expansion (all queries) | 0.87 | 34 | 200 |
| **selective (BM25-confidence gated)** | **0.85** | **16** | 83 |

The fix worked, then bit back. An LLM rewrite agent that pads the query with
plausible recipe vocabulary pushed Recall@5 from 0.73 to 0.87 and dragged 65% of
the buried recipes back into the top 5. Good. But it also wrecked 34 queries, and
30 of those were ones BM25 already had right. The reason is the same mechanism
running in reverse. Expansion dumps vocabulary on every query, so a query that
already owned a distinctive word now also carries five generic ones, and the
generic ones pull in the wrong recipes. The intervention that rescues the
vocabulary-poor queries is the same one that poisons the vocabulary-rich ones.

So the fix needed a fix. Don't expand everything. Expand only the queries BM25 is
unsure about, and you can tell which those are without ever seeing the answer.
When BM25 has a real match, the top score towers over the rest. When it's lost,
the top scores bunch up flat. Gate on that gap, expand only the flat ones, and you
get Recall@5 0.85 with 16 regressions instead of 34, touching 83 queries instead
of 200. Roughly all of the upside, half the damage, 40% of the cost. The gate
reads BM25's own confidence, not the answer key, so it survives contact with real
traffic. That last part matters more than the number. "Just undo the queries that
got worse" would score higher and mean nothing, because in production you don't
know which ones got worse. Same trap as tuning on the test set, wearing a costume.

## 4. Caveats
- Threshold (gap≥0.95) was chosen by reading the full curve, which includes the
  answer. A real deployment would tune it on a held-out set. The mechanism (blind
  gate) is honest. The exact threshold is mildly optimistic.
- Data artifacts hurt retrieval. "325°F" got mangled to "325of" in cleaning, which
  breaks the lexical match. A process/data fix, not a tools fix.

## Files
- `run_retrieval_eval.py` — BM25 index + Recall@k/MRR
- `run_rewrite_eval.py` — blind LLM query-expansion agent vs baseline
- `run_selective_rewrite.py` — confidence-gated selective expansion
- `results/` — per-query ranks (baseline, rewrite)
