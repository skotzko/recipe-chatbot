"""Build the HW2 Part 2 open-coding workspace.

Takes the course's 250-pair query_response.jsonl and produces a finite,
reproducible working set for open coding:

  1. open_coding_sample.md  -- human-readable review doc. One section per
     trace: the user query + the FULL bot response + a blank notes block.
     This is what you actually read and annotate while open coding.

  2. error_analysis.csv     -- the structured tracking sheet (course's
     Part 2 Step 4 column scheme). Pre-populated with the sampled
     Trace_ID + User_Query so you only have to fill in your summary /
     notes / per-failure-mode columns AFTER reading. Preserves the
     UTF-8 BOM the original attempt1 file shipped with.

Sampling is SEEDED (random.seed(42)) so the 40-trace set is identical on
every run -- you can stop and resume open coding without the working set
shifting under you. Re-run only changes output if SAMPLE_N / SEED change.

Usage (from this directory):
    python build_open_coding_workspace.py
"""

import csv
import io
import json
import random
from pathlib import Path

HERE = Path(__file__).parent
JSONL = HERE.parent / "reference_files" / "query_response.jsonl"

SEED = 42
SAMPLE_N = 40  # readable, finishable first-pass open-coding volume

MD_OUT = HERE / "open_coding_sample.md"
CSV_OUT = HERE / "error_analysis.csv"
CSV_BOM = "﻿"  # match the BOM the original attempt1 csv shipped with


def load_pairs():
    pairs = []
    with JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))
    return pairs


def sample(pairs):
    rng = random.Random(SEED)
    picks = rng.sample(pairs, k=min(SAMPLE_N, len(pairs)))
    # Stable, readable order in the outputs: sort by id.
    picks.sort(key=lambda p: p["id"])
    return picks


def write_markdown(picks):
    lines = [
        "# HW2 Part 2 — Open Coding Worksheet",
        "",
        f"Seeded random sample of **{len(picks)}** traces "
        f"(seed={SEED}) from the course's 250-pair "
        "`reference_files/query_response.jsonl`.",
        "",
        "**How to use this file (open coding, README Part 2 Step 2):**",
        "",
        "> Read each trace. In the `NOTES` block, write what you observe —"
        " patterns, errors, anything unusual. Do NOT assign categories yet."
        " Just observe. Categories come later in axial coding (Step 3).",
        "",
        "After a pass through here, transfer observations into"
        " `error_analysis.csv` and synthesize failure modes into"
        " `../reference_files/failure_mode_taxonomy.md`.",
        "",
        "---",
        "",
    ]
    for i, p in enumerate(picks, 1):
        lines += [
            f"## {i}. `{p['id']}`",
            "",
            "**User query:**",
            "",
            f"> {p['query']}",
            "",
            "**Bot response:**",
            "",
            "```text",
            p["response"],
            "```",
            "",
            "**NOTES:**",
            "",
            "_(open-coding observations — leave uncategorized)_",
            "",
            "---",
            "",
        ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def write_csv(picks):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        ["Trace_ID", "User_Query", "Full_Bot_Trace_Summary", "Open_Code_Notes"]
    )
    for p in picks:
        w.writerow([p["id"], p["query"], "", ""])
    # Preserve the original file's UTF-8 BOM, drop the trailing newline
    # csv.writer adds, to keep the byte shape close to the shipped header.
    CSV_OUT.write_text(CSV_BOM + buf.getvalue().rstrip("\r\n"), encoding="utf-8")


def main():
    pairs = load_pairs()
    picks = sample(pairs)
    write_markdown(picks)
    write_csv(picks)
    print(f"Loaded {len(pairs)} pairs from {JSONL.name}")
    print(f"Sampled {len(picks)} (seed={SEED})")
    print(f"  -> {MD_OUT.relative_to(HERE.parent)}")
    print(f"  -> {CSV_OUT.relative_to(HERE.parent)}")
    print("IDs:", ", ".join(p["id"] for p in picks))


if __name__ == "__main__":
    main()
