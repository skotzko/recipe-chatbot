"""Optional HW4: LLM query-rewrite agent vs. baseline BM25.

The rewrite agent is BLIND to the target recipe (as it must be at inference time):
it sees only the user query and rewrites it to include terms likely to appear in
recipe text. We then retrieve with the SAME BM25 index and compare to baseline.

This is a direct test of the Step-5 finding: failures lack distinctive tokens.
If injecting plausible recipe vocabulary lifts recall (esp. on generic-vocab
queries), the diagnosis holds. If not, it's incomplete.

Usage:
    python run_rewrite_eval.py --workers 6
"""
from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import litellm
from dotenv import load_dotenv

# reuse the EXACT baseline index + scoring so the only variable is the query text
from run_retrieval_eval import HERE, REF, load, build_index, tokenize  # noqa: E402

load_dotenv(HERE.parent.parent / ".env")
MODEL = os.environ.get("HW4_REWRITE_MODEL", "openai/gpt-4.1-nano")

REWRITE_PROMPT = """You are improving a search query for a recipe database that uses keyword \
matching. The user's query is often vague and uses generic words. Rewrite it into a \
keyword-rich search query that includes specific terms LIKELY to appear in the target \
recipe's text (ingredients, techniques, dish names, cuisines). Add plausible related \
cooking terms even if the user didn't say them. Do NOT answer the question. Output ONLY \
the rewritten search query, nothing else.

User query: {query}
Rewritten search query:"""


def rewrite(query: str) -> str:
    try:
        resp = litellm.completion(
            model=MODEL,
            messages=[{"role": "user", "content": REWRITE_PROMPT.format(query=query)}],
            temperature=0,
            num_retries=6,
            timeout=60,
        )
        out = resp["choices"][0]["message"]["content"].strip()
        return out or query
    except Exception as e:  # noqa: BLE001
        return query  # fall back to original on failure (no crash)


def rank_of_source(bm25, recipe_ids, query_text, source_id):
    scores = bm25.get_scores(tokenize(query_text))
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    for rank, idx in enumerate(order, start=1):
        if recipe_ids[idx] == source_id:
            return rank
    return None


def metrics(ranks):
    n = len(ranks)
    return {
        "R@1": sum(1 for r in ranks if r == 1) / n,
        "R@3": sum(1 for r in ranks if r <= 3) / n,
        "R@5": sum(1 for r in ranks if r <= 5) / n,
        "MRR": sum(1.0 / r for r in ranks) / n,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default="results/rewrite_per_query.jsonl")
    args = ap.parse_args()

    recipes, queries = load()
    bm25, recipe_ids = build_index(recipes)
    print(f"rewrite model: {MODEL}")
    print(f"queries: {len(queries)}  (rewriting all, blind to target)\n")

    # rewrite all queries in parallel
    def do(i_q):
        i, q = i_q
        return i, rewrite(q["query"])

    rewritten = {}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(do, (i, q)) for i, q in enumerate(queries)]
        done = 0
        for f in as_completed(futs):
            i, rw = f.result()
            rewritten[i] = rw
            done += 1
            if done % 50 == 0 or done == len(queries):
                print(f"  rewritten {done}/{len(queries)}")

    rows = []
    for i, q in enumerate(queries):
        base_rank = rank_of_source(bm25, recipe_ids, q["query"], q["source_recipe_id"])
        rw_rank = rank_of_source(bm25, recipe_ids, rewritten[i], q["source_recipe_id"])
        rows.append({
            "source_recipe_id": q["source_recipe_id"],
            "source_recipe_name": q.get("source_recipe_name"),
            "base_rank": base_rank,
            "rewrite_rank": rw_rank,
            "delta": (base_rank - rw_rank) if (base_rank and rw_rank) else None,
            "original_query": q["query"],
            "rewritten_query": rewritten[i],
        })

    base_m = metrics([r["base_rank"] for r in rows])
    rw_m = metrics([r["rewrite_rank"] for r in rows])

    print("\n=== baseline vs rewrite ===")
    print(f"{'metric':6} {'baseline':>9} {'rewrite':>9} {'delta':>8}")
    for k in ["R@1", "R@3", "R@5", "MRR"]:
        print(f"{k:6} {base_m[k]:>9.3f} {rw_m[k]:>9.3f} {rw_m[k]-base_m[k]:>+8.3f}")

    helped = sum(1 for r in rows if r["delta"] and r["delta"] > 0)
    hurt = sum(1 for r in rows if r["delta"] and r["delta"] < 0)
    same = sum(1 for r in rows if r["delta"] == 0)
    print(f"\nper-query: helped {helped}, hurt {hurt}, unchanged {same}")

    out = HERE / args.out
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
