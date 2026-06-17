"""BM25 retrieval eval for Recipe Bot (HW4, option 3).

Indexes the 200 processed recipes by their full_text, runs each of the 200
synthetic queries, and checks whether the query's source recipe is retrieved.

Metrics: Recall@1, Recall@3, Recall@5, MRR.
Per-query results (rank of the true recipe) are saved for slicing in Step 5.

Usage:
    python run_retrieval_eval.py                # baseline BM25
    python run_retrieval_eval.py --out results/baseline.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

HERE = Path(__file__).parent
REF = HERE / "reference_files"


def tokenize(text: str) -> list[str]:
    """Simple, transparent tokenization: lowercase + alphanumeric word split.
    Kept deliberately plain so retrieval failures reflect lexical mismatch,
    not tokenizer cleverness."""
    return re.findall(r"[a-z0-9]+", text.lower())


def load():
    recipes = json.load(open(REF / "processed_recipes.json"))
    queries = [json.loads(l) for l in open(REF / "synthetic_queries.jsonl")]
    return recipes, queries


def build_index(recipes: list[dict]):
    corpus_tokens = [tokenize(r["full_text"]) for r in recipes]
    bm25 = BM25Okapi(corpus_tokens)
    recipe_ids = [r["id"] for r in recipes]
    return bm25, recipe_ids


def rank_of_source(bm25, recipe_ids, query_text, source_id) -> int | None:
    """Return the 1-based rank of the source recipe in the BM25 ranking, or None
    if it somehow isn't present (shouldn't happen — whole corpus is ranked)."""
    scores = bm25.get_scores(tokenize(query_text))
    # indices sorted by descending score
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    for rank, idx in enumerate(order, start=1):
        if recipe_ids[idx] == source_id:
            return rank
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/baseline_per_query.jsonl")
    ap.add_argument("--k", type=int, nargs="+", default=[1, 3, 5],
                    help="recall@k cutoffs to report")
    args = ap.parse_args()

    recipes, queries = load()
    bm25, recipe_ids = build_index(recipes)

    rows = []
    for q in queries:
        rank = rank_of_source(bm25, recipe_ids, q["query"], q["source_recipe_id"])
        rows.append({
            "source_recipe_id": q["source_recipe_id"],
            "source_recipe_name": q.get("source_recipe_name"),
            "rank": rank,                       # 1-based rank of the true recipe
            "tags": q.get("tags", []),
            "query": q["query"],
        })

    n = len(rows)
    # Recall@k = fraction of queries whose true recipe ranks within top k
    recalls = {k: sum(1 for r in rows if r["rank"] is not None and r["rank"] <= k) / n
               for k in args.k}
    # MRR = mean of 1/rank (0 if not found at all)
    mrr = sum((1.0 / r["rank"]) if r["rank"] else 0.0 for r in rows) / n

    print(f"queries: {n}  recipes: {len(recipes)}")
    print(f"tokenization: lowercase alphanumeric split (baseline)\n")
    for k in args.k:
        print(f"Recall@{k}: {recalls[k]:.3f}")
    print(f"MRR     : {mrr:.3f}")

    # rank distribution, useful for Step 5
    found = [r["rank"] for r in rows if r["rank"]]
    print(f"\nfound in top-1: {sum(1 for x in found if x==1)}")
    print(f"never in top-5: {sum(1 for r in rows if not r['rank'] or r['rank']>5)}")
    print(f"worst ranks   : {sorted(found, reverse=True)[:5]}")

    out = HERE / args.out
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"\nwrote per-query results -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
