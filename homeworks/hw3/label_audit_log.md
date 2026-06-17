# Dev Label Audit Log

Audited the dev traces where the judge **disagreed** with my HW2 labels
(true=FAIL, pred=PASS — the judge's "missed failures"). Reading them before
editing the prompt revealed that most disagreements were *label* problems, not
judge problems.

## Changes

| trace_id | restriction | action | from | to | reason |
|----------|-------------|--------|------|----|--------|
| 26_4  | sugar-free | **keep FAIL** | FAIL | FAIL | Real violation: recipe used honey in a sugar-free dish. Genuine judge miss → fixed in prompt (added "including honey" + ingredient-family generalization rule). |
| 47_31 | dairy-free | **relabel** | FAIL | PASS | User conditionally waived the restriction ("cheese is okay sometimes"). Bot offered cheese as OPTIONAL, leaving the choice to the user — threads the needle = adherent. Original FAIL was an annotation error; judge was correct. |
| 51_31 | whole30 | **exclude** | FAIL | (removed) | No dietary restriction stated in the user query ("I eat pretty clean most of the time"). The whole30 tag was dataset-injected, never user-requested. Invalid case for a dietary-*adherence* judge. Moved to `dev_excluded.jsonl` with reason. Out of scope (would belong to a separate clarification/ambiguity judge). |

## Effect on the set
- dev.jsonl: 40 → 39 rows (1 excluded)
- 1 label flipped FAIL → PASS

## Takeaway (for the write-up)
Reading 3 judge-disagreement traces surfaced **2 label issues out of 3** (1 wrong
label, 1 invalid trace) and only **1 true judge miss**. Implications:
1. My labels are noisier than assumed. Judge agreement does NOT confirm a label —
   only disagreements were audited, so the agreeing rows may hide same-direction errors.
2. judgy corrects judge-vs-label disagreement but **treats labels as ground truth**;
   residual label noise propagates into θ̂ uncorrected. Report final metrics with that caveat.
3. Test labels carry the same noise. Not re-audited here (exercise scope), but in
   production this audit would extend to the full set before trusting any number.

---

# Judge Frozen

After iterating on dev (39 traces, measured with `run_judge.py --repeat 5`), the
judge prompt is **frozen**. No further prompt edits before the test run.

## Final dev performance (5 runs, PASS=positive)
- **TNR (catch FAILs): 1.000, spread 0.000** — catches every violation, reliably.
- **TPR (pass PASSes): 0.929, spread 0.065** — occasionally over-strict on compliant recipes.

## Prompt changes that got us here
1. `(including honey)` on the sugar-free definition + ingredient-intent generalization line.
2. FAIL rule: a non-compliant ingredient offered as an *option/alternative* is still a FAIL,
   UNLESS the user explicitly permitted it (distinguishes 26 honey-FAIL from 47 cheese-PASS).
3. Scope rule (above PASS/FAIL): the given restriction ALWAYS applies even if the user's query
   doesn't restate it (fixed the chicken-in-vegetarian flippers 43_14, 38_22). This single rule
   collapsed TNR spread 0.25 → 0.00.
4. Removed the "must ask clarifying questions" clause — clarification is a *different* judge's
   job (out of scope for a dietary-adherence judge); it also contradicted the 47 PASS decision.

## Freeze rationale (the tradeoff)
Driving the scope rule up cost some TPR (0.96 → 0.93): the judge now occasionally false-fails a
compliant recipe. **This is the safe direction to err.** For a dietary-*safety* judge, a missed
violation (FAIL→PASS) can hurt someone (e.g. an allergen reaching an allergic user), whereas a
false alarm (PASS→FAIL) just gets a fine recipe a second look. So we deliberately traded a
harmless error to eliminate a harmful one, and locked TNR at 1.0. Chasing the remaining TPR
flippers (29_7, 16_36) would risk loosening the FAIL side — not worth it.

## Skepticism caveat
TNR=1.000 on dev is partly overfit to only 8 dev FAILs (tuned against this set). Expect test
TNR to be lower. The honest measure is the held-out test run, reported next.
