"""Final HW3 scoring: correct the judge's bias with judgy to estimate the bot's
true dietary-adherence rate (theta_hat) + 95% CI.

Inputs (all PASS=1, FAIL=0):
  - test_labels    : human labels on the 46 test traces  (reference_files/test.jsonl)
  - test_preds     : frozen judge's verdicts on those 46 (test_preds.jsonl)
  - unlabeled_preds: frozen judge's verdicts on the 2,400 raw traces (unlabeled_preds.jsonl)
"""
from __future__ import annotations
import json
from pathlib import Path

from judgy import estimate_success_rate

HERE = Path(__file__).parent
REF = HERE / "reference_files"


def enc(label: str) -> int:
    return 1 if label == "PASS" else 0


def main() -> int:
    # test set: align labels and judge preds by trace_id
    test_traces = {json.loads(l)["trace_id"]: json.loads(l)
                   for l in open(REF / "test.jsonl")}
    test_pred_rows = [json.loads(l) for l in open(HERE / "test_preds.jsonl")]

    test_labels, test_preds = [], []
    test_label_by_tid = {t: r["label"] for t, r in test_traces.items()}
    # test_preds.jsonl rows are in test.jsonl order; match defensively by query_id+index
    test_order = [json.loads(l) for l in open(REF / "test.jsonl")]
    for ref, pr in zip(test_order, test_pred_rows):
        if pr["pred"] is None:
            continue  # drop unparsed (shouldn't happen on test)
        test_labels.append(enc(ref["label"]))
        test_preds.append(enc(pr["pred"]))

    # unlabeled pool
    unl_rows = [json.loads(l) for l in open(HERE / "unlabeled_preds.jsonl")]
    unlabeled_preds = [enc(r["pred"]) for r in unl_rows if r["pred"] is not None]
    n_unparsed = sum(1 for r in unl_rows if r["pred"] is None)

    # raw (uncorrected) judge pass rate on the unlabeled pool
    p_obs = sum(unlabeled_preds) / len(unlabeled_preds)

    theta_hat, lo, hi = estimate_success_rate(test_labels, test_preds, unlabeled_preds)

    print("=== Inputs ===")
    print(f"test n           : {len(test_labels)}  (PASS={sum(test_labels)}, FAIL={len(test_labels)-sum(test_labels)})")
    print(f"unlabeled n      : {len(unlabeled_preds)}  (dropped {n_unparsed} unparsed)")
    print()
    print("=== Results ===")
    print(f"Raw judge pass rate  (p_obs) : {p_obs:.3f}")
    print(f"Corrected true rate  (theta) : {theta_hat:.3f}")
    print(f"95% CI                       : [{lo:.3f}, {hi:.3f}]")
    print()
    print(f"Correction (theta - p_obs)   : {theta_hat - p_obs:+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
