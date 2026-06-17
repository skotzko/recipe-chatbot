"""Run the frozen judge over the unlabeled pool (raw_traces.jsonl) to produce
unlabeled_preds for judgy. No labels involved; we only collect PASS/FAIL verdicts.
"""
from __future__ import annotations
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# reuse the exact judge call + prompt the labeled runs used
sys.path.insert(0, str(Path(__file__).parent))
from run_judge import judge_trace, PROMPT_FILE, JUDGE_MODEL, REF  # noqa: E402

OUT = Path(__file__).parent / "unlabeled_preds.jsonl"


def main() -> int:
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

    traces = [json.loads(l) for l in open(REF / "raw_traces.jsonl")]
    if limit:
        traces = traces[:limit]
    system_prompt = PROMPT_FILE.read_text()
    total = len(traces)
    print(f"judge model : {JUDGE_MODEL}")
    print(f"unlabeled pool: raw_traces.jsonl  (n={total})")
    print(f"workers     : {workers}\n")

    def work(job):
        i, t = job
        pred, raw = judge_trace(system_prompt, t)
        return i, {"trace_id": t.get("trace_id"), "query_id": t.get("query_id"),
                   "pred": pred, "raw": raw}

    results: dict[int, dict] = {}
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(work, (i, t)) for i, t in enumerate(traces)]
        for fut in as_completed(futures):
            i, row = fut.result()
            results[i] = row
            done += 1
            if done % 100 == 0 or done == total:
                print(f"  {done}/{total}")

    rows = [results[i] for i in range(total)]
    with open(OUT, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    n_pass = sum(1 for r in rows if r["pred"] == "PASS")
    n_fail = sum(1 for r in rows if r["pred"] == "FAIL")
    n_none = sum(1 for r in rows if r["pred"] is None)
    print(f"\nPASS={n_pass}  FAIL={n_fail}  unparsed={n_none}")
    print(f"raw judge pass-rate = {n_pass}/{n_pass+n_fail} = "
          f"{n_pass/(n_pass+n_fail):.3f}" if (n_pass+n_fail) else "n/a")
    print(f"wrote -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
