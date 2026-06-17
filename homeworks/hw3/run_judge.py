"""Run the LLM judge over a labeled split and report agreement metrics.

Default split is `dev`. The judge prompt is read from llm-judge-prompt.md so the
file you edit IS the judge. Test set is gated behind an explicit --split test and
a confirmation flag, so you cannot burn it by accident.

Usage:
    # iterate here, as many times as you like:
    python run_judge.py                      # -> dev.jsonl, TPR/TNR/confusion
    python run_judge.py --split train        # sanity check on train
    # ONLY when the judge is frozen:
    python run_judge.py --split test --i-am-done-iterating
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import litellm  # type: ignore
from dotenv import load_dotenv

HERE = Path(__file__).parent
REF = HERE / "reference_files"
PROMPT_FILE = HERE / "llm-judge-prompt.md"

load_dotenv(HERE.parent.parent / ".env")

# Default to the course-configured judge (high API rate limits). Override via
# HW3_JUDGE_MODEL or MODEL_NAME_JUDGE in .env. NOTE: a Claude *Max* subscription
# does NOT grant API access -- anthropic/* models bill against your API tier's
# token/min limit (Tier 1 = 30k/min), which throttles this hard.
JUDGE_MODEL = os.environ.get(
    "HW3_JUDGE_MODEL",
    os.environ.get("MODEL_NAME_JUDGE", "openai/gpt-4.1-nano"),
)


def build_messages(system_prompt: str, trace: dict) -> list[dict]:
    """Fill the per-trace input. Restriction is a GIVEN input (matches the prompt's examples)."""
    user = (
        f"<query>{trace['query']}</query>\n"
        f"<dietary_restriction>{trace['dietary_restriction']}</dietary_restriction>\n"
        f"<output>\n{trace['response']}\n</output>\n\n"
        "Respond in JSON only."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user},
    ]


def parse_answer(text: str) -> str | None:
    """Pull PASS/FAIL out of the model's JSON reply, tolerant of stray prose/fences."""
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(0))
            ans = str(obj.get("answer", "")).strip().upper()
            if ans in ("PASS", "FAIL"):
                return ans
        except json.JSONDecodeError:
            pass
    # last-ditch: bare token
    m = re.search(r'\b(PASS|FAIL)\b', text.upper())
    return m.group(1) if m else None


def judge_trace(system_prompt: str, trace: dict) -> tuple[str | None, str]:
    """Call the judge. litellm retries 429s/transient errors with backoff.
    On terminal failure, return (None, "<error>") so one bad row never kills the run."""
    try:
        resp = litellm.completion(
            model=JUDGE_MODEL,
            messages=build_messages(system_prompt, trace),
            temperature=0,
            num_retries=6,          # exponential backoff, handles 429s
            timeout=60,
        )
        text = resp["choices"][0]["message"]["content"]
        return parse_answer(text), text
    except Exception as e:  # noqa: BLE001 - we want to survive any per-row failure
        return None, f"<error: {type(e).__name__}: {e}>"


def _rates(rows: list[dict]) -> dict:
    """PASS = positive = 1 (matches judgy's success convention). Returns counts + rates."""
    tp = fp = tn = fn = unparsed = 0
    for r in rows:
        true, pred = r["true"], r["pred"]
        if pred is None:
            unparsed += 1
            continue
        if true == "PASS" and pred == "PASS":
            tp += 1
        elif true == "FAIL" and pred == "PASS":
            fp += 1
        elif true == "FAIL" and pred == "FAIL":
            tn += 1
        elif true == "PASS" and pred == "FAIL":
            fn += 1
    scored = len(rows) - unparsed
    return {
        "tp": tp, "fp": fp, "tn": tn, "fn": fn, "unparsed": unparsed,
        "scored": scored,
        "acc": (tp + tn) / scored if scored else 0.0,
        "tpr": tp / (tp + fn) if (tp + fn) else float("nan"),  # recall on PASS
        "tnr": tn / (tn + fp) if (tn + fp) else float("nan"),  # recall on FAIL
    }


def metrics(rows: list[dict]) -> None:
    """PASS = positive = 1 (matches judgy's success convention)."""
    m = _rates(rows)
    tp, fp, tn, fn = m["tp"], m["fp"], m["tn"], m["fn"]
    n = len(rows)
    scored, acc, tpr, tnr = m["scored"], m["acc"], m["tpr"], m["tnr"]

    print("\n=== Confusion matrix (positive class = PASS) ===")
    print(f"             pred PASS   pred FAIL")
    print(f"true PASS      {tp:>5}      {fn:>5}   (TP / FN)")
    print(f"true FAIL      {fp:>5}      {tn:>5}   (FP / TN)")
    print("\n=== Metrics ===")
    print(f"n={n}  scored={scored}  unparsed={m['unparsed']}")
    print(f"accuracy : {acc:.3f}")
    print(f"TPR (recall on PASS) : {tpr:.3f}   [judge correctly passes a true PASS]")
    print(f"TNR (recall on FAIL) : {tnr:.3f}   [judge correctly fails a true FAIL]")
    print("\nThese TPR/TNR (PASS=1) feed judgy.estimate_success_rate on the TEST run.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["train", "dev", "test"])
    ap.add_argument("--i-am-done-iterating", action="store_true",
                    help="required to run on the test split")
    ap.add_argument("--limit", type=int, default=None, help="judge only first N (debug)")
    ap.add_argument("--workers", type=int, default=3,
                    help="concurrent judge calls (default 3, tuned for a 30k tok/min "
                         "tier; raise if your Anthropic tier is higher, 1 for serial)")
    ap.add_argument("--out", default=None, help="write per-row predictions to this jsonl")
    ap.add_argument("--repeat", type=int, default=1,
                    help="judge each trace N times to measure variance (default 1)")
    args = ap.parse_args()

    if args.split == "test" and not args.i_am_done_iterating:
        print("REFUSING to run on the TEST set.\n"
              "Test is touched ONCE, after the judge is frozen. Iterate on dev.\n"
              "If you are truly done, re-run with --i-am-done-iterating.", file=sys.stderr)
        return 2

    path = REF / f"{args.split}.jsonl"
    traces = [json.loads(l) for l in open(path)]
    if args.limit:
        traces = traces[: args.limit]
    system_prompt = PROMPT_FILE.read_text()

    print(f"judge model : {JUDGE_MODEL}")
    print(f"split       : {args.split}  (n={len(traces)})")
    print(f"prompt      : {PROMPT_FILE.name}  ({len(system_prompt)} chars)\n")

    # One unit of work = (trace index, repeat index). All flattened so the thread
    # pool parallelizes across both traces and repeats.
    def work(job):
        idx, rep, t = job
        pred, raw = judge_trace(system_prompt, t)
        return idx, rep, {"query_id": t.get("query_id"), "true": t["label"],
                          "pred": pred, "raw": raw}

    jobs = [(i, rep, t) for i, t in enumerate(traces) for rep in range(args.repeat)]
    by_trace: dict[int, list] = {i: [] for i in range(len(traces))}
    done, total = 0, len(jobs)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(work, j) for j in jobs]
        for fut in as_completed(futures):
            idx, rep, row = fut.result()
            by_trace[idx].append(row)
            done += 1
            if args.repeat == 1:
                mark = "ok " if row["pred"] == row["true"] else "DIFF"
                print(f"[{done:>3}/{total}] qid={str(row['query_id']):>3} "
                      f"true={row['true']:>4} pred={str(row['pred']):>4} {mark}")
    if args.repeat > 1:
        print(f"ran {len(traces)} traces x {args.repeat} repeats = {total} judge calls\n")

    if args.repeat == 1:
        rows = [by_trace[i][0] for i in range(len(traces))]
        metrics(rows)
        if args.out:
            with open(args.out, "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            print(f"\nwrote predictions -> {args.out}")
        return 0

    # --- multi-run variance report ---
    per_run_metrics = []
    for rep in range(args.repeat):
        rows = [by_trace[i][rep] for i in range(len(traces))]
        per_run_metrics.append(_rates(rows))
    tprs = [m["tpr"] for m in per_run_metrics]
    tnrs = [m["tnr"] for m in per_run_metrics]

    def fmt(vals):
        v = [x for x in vals if x == x]  # drop nan
        if not v:
            return "n/a"
        return f"mean={sum(v)/len(v):.3f}  min={min(v):.3f}  max={max(v):.3f}  spread={max(v)-min(v):.3f}"

    print("=== Variance across runs (PASS=positive) ===")
    print(f"TPR (pass true-PASS): {fmt(tprs)}")
    print(f"TNR (fail true-FAIL): {fmt(tnrs)}")

    # per-trace stability: which traces flip PASS<->FAIL across repeats?
    # (None/parse-failures are tracked separately, not counted as rubric flips)
    print("\n=== Unstable traces (verdict flips across repeats) ===")
    flips = []
    for i, t in enumerate(traces):
        preds = [r["pred"] for r in by_trace[i] if r["pred"] in ("PASS", "FAIL")]
        if len(set(preds)) > 1:
            n_pass = preds.count("PASS")
            flips.append((t.get("trace_id", t.get("query_id")), t["label"], n_pass, len(preds)))
    if not flips:
        print("(none — judge gave a stable verdict on every trace)")
    else:
        # closest to 50/50 = most unstable = listed first
        for tid, true, n_pass, n in sorted(flips, key=lambda x: abs(x[2] - x[3] / 2)):
            print(f"  {str(tid):>7} true={true:>4}  PASS {n_pass}/{n}, FAIL {n-n_pass}/{n}  <- rubric gap")
        print(f"\n{len(flips)} trace(s) flip verdict. Stabilize them (hard rules in the "
              "prompt) to both raise AND steady the metric.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
