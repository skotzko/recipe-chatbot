"""Build the open-coding worksheet from MY OWN bot's results.

Sibling of build_open_coding_workspace.py. That one samples the
course's 250-pair query_response.jsonl. THIS one reads the results JSON
that scripts/bulk_test.py produced when run on my 50 synthetic queries
(synthetic_queries_expanded.csv) through my HW1 system prompt -- so the
failures I open-code are MY bot's failures.

All 50 traces are included (no sampling -- 50 is a finishable set).

Outputs (distinct names so the course-based worksheet is not clobbered):
  - open_coding_sample_mybot.md   : the worksheet I read + annotate
  - error_analysis_mybot.csv      : tracking sheet (course Step 4 cols)

The results/*.json file is gitignored, so pass its path explicitly:
    python build_open_coding_workspace_mybot.py ../../../results/results_YYYYMMDD_HHMMSS.json
If no path is given, the most recent results/results_*.json is used.
"""

import csv
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
RESULTS_DIR = HERE.parent.parent.parent / "results"

MD_OUT = HERE / "open_coding_sample_mybot.md"
CSV_OUT = HERE / "error_analysis_mybot.csv"
CSV_BOM = "﻿"  # match the BOM the original error_analysis.csv shipped with


def pick_results_file(argv):
    if len(argv) > 1:
        p = Path(argv[1])
        if not p.exists():
            sys.exit(f"results file not found: {p}")
        return p
    candidates = sorted(RESULTS_DIR.glob("results_*.json"))
    if not candidates:
        sys.exit(f"no results_*.json in {RESULTS_DIR} -- run bulk_test.py first")
    return candidates[-1]  # most recent by lexical (timestamped) name


def load_pairs(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        sys.exit(f"unexpected JSON shape in {path} (expected a list)")
    # stable order by integer id where possible
    def keyf(r):
        try:
            return (0, int(r["id"]))
        except (KeyError, ValueError):
            return (1, str(r.get("id")))
    return sorted(data, key=keyf)


def write_markdown(pairs, src_name):
    lines = [
        "# HW2 Part 2 — Open Coding Worksheet (my bot)",
        "",
        f"All **{len(pairs)}** traces from my own Recipe Bot — my 50 "
        "synthetic queries (`synthetic_queries_expanded.csv`) run through "
        f"my HW1 system prompt. Source: `results/{src_name}`.",
        "",
        "**How to use this file — open coding, course reader Sec 3.2"
        " (grounded theory):**",
        "",
        "> For each trace, read the whole thing and write free-form notes"
        " in your own words about what's wrong or surprising. These are"
        " **single-turn** traces, so note **all** failure modes you see,"
        " not just the first. (The 'point of first failure only' rule is"
        " for multi-turn / multi-component traces with tool calls — per"
        " the instructors, it doesn't apply here.) Do NOT assign"
        " categories yet — grouping happens later in axial coding."
        " Optionally force a binary acceptable/unacceptable call (pick a"
        " side even if borderline; it sharpens your criteria).",
        "",
        "> Write **complete sentences** and **quote the offending text** —"
        " you'll feed these notes to an LLM for axial coding, and you'll"
        " need to re-read them yourself. Judge against your HW1 system"
        " prompt's own promises, and read as your target user (a beginner"
        " cook): the same output can be fine for one audience and a"
        " failure for another.",
        "",
        "> Pitfall to avoid (Sec 3.7): don't reach for generic labels"
        " ('hallucination', 'verbosity'). Describe the *specific*,"
        " app-specific thing this recipe bot did wrong.",
        "",
        "After a pass through here, transfer observations into"
        " `error_analysis_mybot.csv` and synthesize failure modes into"
        " `../reference_files/failure_mode_taxonomy.md`.",
        "",
        "---",
        "",
    ]
    for i, p in enumerate(pairs, 1):
        lines += [
            f"## {i}.",
            "",
            f"_Trace ID: `{p['id']}`_",
            "",
            "**User query:**",
            "",
            f"> {p['query']}",
            "",
            "**Bot response:**",
            "",
            "```text",
            p.get("response", "") or "(empty response)",
            "```",
            "",
            "**Observations:**",
            "",
            "_(single-turn — note ALL failures you see, not just the "
            "first. Complete sentences, quote the offending text. "
            "Specific + app-specific; no generic labels. Uncategorized.)_",
            "",
            "",
            "**Acceptable? (optional):**",
            "",
            "_(yes / no — force a side even if borderline)_",
            "",
            "",
            "---",
            "",
        ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def write_csv(pairs):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Trace_ID", "User_Query", "Full_Bot_Trace_Summary", "Open_Code_Notes"])
    for p in pairs:
        w.writerow([p["id"], p["query"], "", ""])
    CSV_OUT.write_text(CSV_BOM + buf.getvalue().rstrip("\r\n"), encoding="utf-8")


def main(argv):
    src = pick_results_file(argv)
    pairs = load_pairs(src)
    write_markdown(pairs, src.name)
    write_csv(pairs)
    print(f"Loaded {len(pairs)} traces from results/{src.name}")
    print(f"  -> {MD_OUT.relative_to(HERE.parent)}")
    print(f"  -> {CSV_OUT.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main(sys.argv)
