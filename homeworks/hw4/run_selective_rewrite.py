"""Selective query expansion gated on BM25 confidence (HW4 improvement experiment).

Idea (decided BLIND, i.e. using only inference-time signals, not the answer):
  1. Run baseline BM25.
  2. If BM25 is CONFIDENT on a query (clear top-1 winner), keep the baseline result.
     If BM25 is UNCONFIDENT (flat top scores -> no distinctive anchor), use the
     EXPANDED query instead.
  3. Measure recall + regressions vs. baseline and vs. blanket-expansion.

Confidence signal = gap ratio between the #1 and #2 BM25 scores for the ORIGINAL
query. score2/score1 near 1.0 = flat = unconfident -> expand. This uses only the
query's own score shape, which a live system also has. The true rank is NEVER
consulted to make the expand/keep decision (that would leak the answer).

No new LLM calls: reuses rewritten queries from results/rewrite_per_query.jsonl.
"""
from __future__ import annotations

import json
from pathlib import Path

from run_retrieval_eval import HERE, REF, load, build_index, tokenize  # noqa: E402

REWRITE_FILE = HERE / "results" / "rewrite_per_query.jsonl"


def top2_scores(bm25, query_text):
    scores = sorted(bm25.get_scores(tokenize(query_text)), reverse=True)
    s1 = scores[0] if scores else 0.0
    s2 = scores[1] if len(scores) > 1 else 0.0
    return s1, s2


def rank_of_source(bm25, recipe_ids, query_text, source_id):
    scores = bm25.get_scores(tokenize(query_text))
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    for rank, idx in enumerate(order, start=1):
        if recipe_ids[idx] == source_id:
            return rank
    return None


def recall_mrr(ranks):
    n = len(ranks)
    return (
        sum(1 for r in ranks if r <= 1) / n,
        sum(1 for r in ranks if r <= 3) / n,
        sum(1 for r in ranks if r <= 5) / n,
        sum(1.0 / r for r in ranks) / n,
    )


def main() -> int:
    recipes, queries = load()
    bm25, recipe_ids = build_index(recipes)
    rw = {json.loads(l)["source_recipe_id"]: json.loads(l) for l in open(REWRITE_FILE)}

    # Precompute, per query: baseline rank, expanded rank, and the BLIND confidence
    # signal (gap ratio s2/s1 on the ORIGINAL query). High ratio = flat = unconfident.
    per = []
    for q in queries:
        sid = q["source_recipe_id"]
        s1, s2 = top2_scores(bm25, q["query"])
        gap_ratio = (s2 / s1) if s1 > 0 else 1.0  # 1.0 = totally flat
        per.append({
            "sid": sid,
            "base_rank": rw[sid]["base_rank"],
            "rw_rank": rw[sid]["rewrite_rank"],
            "gap_ratio": gap_ratio,
        })

    base_ranks = [p["base_rank"] for p in per]
    blanket_ranks = [p["rw_rank"] for p in per]

    print(f"{'strategy':28} {'R@1':>5} {'R@3':>5} {'R@5':>5} {'MRR':>5} {'expanded':>9} {'regress':>8}")

    def report(name, ranks, expanded_mask):
        r1, r3, r5, mrr = recall_mrr(ranks)
        n_exp = sum(expanded_mask) if expanded_mask else 0
        # regressions = queries that got WORSE than baseline under this strategy
        regress = sum(1 for r, b in zip(ranks, base_ranks) if r > b)
        print(f"{name:28} {r1:>5.2f} {r3:>5.2f} {r5:>5.2f} {mrr:>5.2f} {n_exp:>9} {regress:>8}")

    report("baseline (no expand)", base_ranks, [False] * len(per))
    report("blanket expand (all)", blanket_ranks, [True] * len(per))

    # Sweep the confidence gate: expand only the LEAST confident queries (gap_ratio
    # above threshold). Lower threshold = expand more.
    for thr in [0.85, 0.90, 0.93, 0.95, 0.97, 0.99]:
        ranks = []
        mask = []
        for p in per:
            expand = p["gap_ratio"] >= thr
            mask.append(expand)
            ranks.append(p["rw_rank"] if expand else p["base_rank"])
        report(f"selective (gap>= {thr:.2f})", ranks, mask)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
