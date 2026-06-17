# HW3 Results — LLM-as-Judge for Dietary Adherence

## 1. Data split (stratified by label, seed=42)
| split | n | PASS | FAIL | fail rate |
|-------|----|------|------|-----------|
| train | 15 | 11 | 4 | 27% |
| dev   | 39* | — | — | — |
| test  | 46 | — | — | — |

\* dev started at 40; 1 trace excluded during label audit (see `label_audit_log.md`).
Test set was quarantined throughout — never read or tuned against.

## 2. Judge performance (held-out TEST, frozen prompt, 5 runs)
| metric | mean | spread |
|--------|------|--------|
| TPR (correctly pass true PASS) | 1.000 | 0.000 |
| TNR (correctly fail true FAIL) | 0.583 | 0.000 |

Compare to dev (the set tuned against): TNR 1.000 / TPR 0.929.
**The dev→test TNR gap (1.000 → 0.583) is overfitting, measured.**

## 3. Final evaluation with judgy (unlabeled pool = 2,400 raw traces)
Unlabeled pool: 2,400 raw traces, 112 unparsed dropped → 2,288 scored.
- Raw judge pass rate (p_obs): 0.894
- Corrected true rate (θ̂):     0.818
- 95% CI:                       [0.628, 0.877]
- Correction (θ̂ − p_obs):      −0.076

## 4. Analysis (1–2 paragraphs) — TODO (write yourself)
Points the data supports, for you to turn into prose:
- Judge is conservative-leaning by design: TNR prioritized over TPR because a missed
  dietary violation can harm an allergic user, while a false alarm is harmless.
- Test TNR 0.583 means the judge misses ~42% of real failures on unseen data → the raw
  judge pass rate OVER-states the bot's true adherence; judgy corrects downward for this.
- Label noise: auditing 3 dev disagreements found 2 label issues (1 wrong, 1 invalid) vs
  1 true judge miss. judgy treats labels as ground truth, so residual label noise in the
  (un-audited) test labels propagates into θ̂ uncorrected — a caveat on the final number.
