"""Goal-completion eval for recipe-agent traces (HW5 follow-on, reference design).

WHY THIS EXISTS
---------------
The heat-map found WHERE the agent breaks. Reading the traces found a bug the
heat-map structurally cannot see: the agent fails GRACEFULLY. After an empty recipe
search it asks a smooth follow-up question, the user stays happy, and the original
goal (get a recipe) quietly dies. User-sentiment signals never catch this, because
the user wasn't unhappy, they were redirected. A thumbs-down misses it too.

The only instrument that catches a graceful failure is a GOAL-COMPLETION check run
on the trace itself: "was the thing the user asked for actually delivered?" -- judged
against the ORIGINAL request, never the redirected one.

TWO-LAYER DESIGN (cheap-and-deterministic first, expensive-and-LLM only for the rest)
------------------------------------------------------------------------------------
Layer 1  CODE eval (free, fast, deterministic):
         Did the trace reach DeliverResponse with a recipe in hand? If it died at or
         before GetRecipes, no recipe was ever delivered -> auto-fail. No LLM needed.
         This resolves the gross misses (in this dataset, all of them).

Layer 2  LLM JUDGE (only for traces that PASS layer 1):
         A trace can deliver SOMETHING that still doesn't satisfy the request --
         gluten in a "gluten-free" ask, lunch when "dinner" was requested. Code can't
         read that. An LLM judge compares the delivered recipe against the original
         goal and returns {reasoning, goal_met}. This is the HW3 judge re-aimed.
         Like any judge, it must be VALIDATED on hand-labeled traces (TPR/TNR) before
         you trust its number -- an unvalidated judge is a vibe with a JSON schema.

THE HARD PART: anchor on the ORIGINAL intent.
Users change the request after a failure (here: "no beans" after the recipe miss). If
you judge goal-completion against the LATEST turn, a graceful redirect that buries the
original goal would PASS -- the exact failure we're hunting. So goal extraction reads
the FIRST user turn, and the judge is told to ignore later goalpost-moving.

This file runs Layer 1 on the HW5 traces today (no API key needed) and ships Layer 2
as a wired-but-gated stub you can turn on with an LLM key.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "reference_files" / "raw_traces.jsonl"
LABELED = HERE / "reference_files" / "labeled_traces.jsonl"

PIPELINE_STATES = [
    "ParseRequest", "PlanToolCalls", "GenCustomerArgs", "GetCustomerProfile",
    "GenRecipeArgs", "GetRecipes", "GenWebArgs", "GetWebInfo",
    "ComposeResponse", "DeliverResponse",
]
IDX = {s: i for i, s in enumerate(PIPELINE_STATES)}


# ---------------------------------------------------------------------------
# Goal extraction: pin down what success means, from the ORIGINAL request only.
# ---------------------------------------------------------------------------
def original_request(trace: dict) -> str:
    """First user turn = the goal we hold the agent to. Later turns may be the agent's
    redirect succeeding; we deliberately do NOT let those move the goalposts."""
    for m in trace["messages"]:
        if m.get("role") == "user":
            return str(m.get("content", "")).strip()
    return ""


# ---------------------------------------------------------------------------
# Layer 1: CODE eval. Deterministic, free. "Did a recipe actually get delivered?"
# ---------------------------------------------------------------------------
def delivered_recipe(trace: dict) -> bool:
    """True iff the agent reached DeliverResponse without an error there.

    Signal: a DeliverResponse tool-call line that does NOT contain an error. We read
    the message stream rather than the label so this works on un-labeled production
    traffic too (the label won't exist live; the trace will)."""
    for m in trace["messages"]:
        c = str(m.get("content", ""))
        if "TOOL_CALL[DeliverResponse]" in c:
            return "error" not in c.lower()
    return False


def layer1_code_eval(trace: dict) -> dict:
    """Cheap structural verdict. completed=False here is a HARD fail -- no recipe
    reached the user, regardless of how pleasant the conversation stayed."""
    delivered = delivered_recipe(trace)
    return {
        "completed": delivered,
        "reason": "reached DeliverResponse with a recipe"
                  if delivered else "no recipe was ever delivered to the user",
    }


# ---------------------------------------------------------------------------
# Layer 2: LLM JUDGE. Only runs on traces that pass Layer 1. Same shape as the HW3
# dietary judge: it reads the delivered answer against the ORIGINAL request and rules
# Pass/Fail on intent satisfaction. Gated behind an explicit flag + API key.
# ---------------------------------------------------------------------------
JUDGE_PROMPT = """You are evaluating whether a recipe assistant satisfied the user's \
ORIGINAL request. Judge ONLY against the original request below. If the conversation \
later shifted to a different ask, IGNORE the shift -- a smooth redirect that abandons \
the original goal is a FAILURE, not a success.

ORIGINAL REQUEST:
{request}

WHAT THE AGENT DELIVERED:
{delivered}

Did the delivered recipe satisfy every stated constraint in the ORIGINAL request \
(dish type, dietary restriction, serving size, etc.)? Respond as JSON:
{{"reasoning": "<one or two sentences>", "goal_met": true or false}}"""


def delivered_text(trace: dict) -> str:
    """The agent's final user-facing message (what the user actually saw)."""
    for m in reversed(trace["messages"]):
        if m.get("role") == "agent" and "TOOL_CALL[" not in str(m.get("content", "")):
            return str(m.get("content", "")).strip()
    return ""


def layer2_llm_judge(trace: dict, model: str) -> dict:
    """Intent-satisfaction verdict. Lazy-imports litellm so Layer 1 runs with no deps."""
    import litellm
    prompt = JUDGE_PROMPT.format(
        request=original_request(trace),
        delivered=delivered_text(trace),
    )
    resp = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        num_retries=6,
        timeout=60,
    )
    out = resp["choices"][0]["message"]["content"].strip()
    try:
        m = re.search(r"\{.*\}", out, re.DOTALL)
        return json.loads(m.group(0)) if m else {"reasoning": out, "goal_met": None}
    except Exception:  # noqa: BLE001
        return {"reasoning": out, "goal_met": None}


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true",
                    help="run Layer 2 LLM judge on traces that pass Layer 1 (needs API key)")
    ap.add_argument("--model", default=os.environ.get("HW5_JUDGE_MODEL", "openai/gpt-4.1-nano"))
    args = ap.parse_args()

    traces = [json.loads(l) for l in open(RAW) if l.strip()]
    print(f"loaded {len(traces)} traces\n")

    completed = failed = 0
    judged_fail = 0
    for t in traces:
        v1 = layer1_code_eval(t)
        if not v1["completed"]:
            failed += 1
            continue
        # passed the cheap check -> only now is the expensive judge worth running
        if args.judge:
            v2 = layer2_llm_judge(t, args.model)
            if v2.get("goal_met"):
                completed += 1
            else:
                judged_fail += 1
        else:
            completed += 1  # structural pass; intent unverified without --judge

    n = len(traces)
    print("=== Layer 1 (code): did a recipe get delivered? ===")
    print(f"  delivered     : {completed + judged_fail}")
    print(f"  never delivered: {failed}   <- graceful-failure traces live here")
    if args.judge:
        print("\n=== Layer 2 (LLM judge): did it satisfy the ORIGINAL request? ===")
        print(f"  goal met   : {completed}")
        print(f"  goal missed: {judged_fail}   <- delivered something, but not what was asked")
    print(f"\ngoal-completion rate: {completed}/{n} = {completed/n:.1%}")
    print("\nNote: user sentiment is never consulted. A pleasant follow-up after an")
    print("empty search counts as a FAILURE here, which is the whole point.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
