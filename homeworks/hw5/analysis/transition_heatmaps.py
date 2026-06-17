#!/usr/bin/env python3
"""HW5 Failure Transition Heatmap Generator (Student-facing)

Reads `labeled_traces.jsonl`, tallies transitions (last_success_state →
first_failure_state), and renders a heat-map PNG.

Usage
-----
$ python analysis/transition_heatmaps.py  # from homeworks/hw5/

Outputs
-------
results/failure_transition_heatmap.png
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------------------------------------------------
# Configuration – keep in sync with generation/generate_traces.py
# -----------------------------------------------------------------------------

PIPELINE_STATES: List[str] = [
    "ParseRequest",
    "PlanToolCalls",
    "GenCustomerArgs",
    "GetCustomerProfile",
    "GenRecipeArgs",
    "GetRecipes",
    "GenWebArgs",
    "GetWebInfo",
    "ComposeResponse",
    "DeliverResponse",
]
STATE_INDEX: Dict[str, int] = {s: i for i, s in enumerate(PIPELINE_STATES)}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "reference_files" / "labeled_traces.jsonl"
OUTPUT_DIR = ROOT / "results"
OUTPUT_PNG = OUTPUT_DIR / "failure_transition_heatmap.png"
OUTPUT_PNG_MARGINS = OUTPUT_DIR / "failure_transition_heatmap_margins.png"


def load_labeled_traces() -> List[Dict]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Expecting {DATA_FILE} – see reference_files/.")
    traces = []
    with open(DATA_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                traces.append(json.loads(line))
    return traces


def build_transition_matrix(traces: List[Dict]) -> np.ndarray:
    n = len(PIPELINE_STATES)
    m = np.zeros((n, n), dtype=int)

    for t in traces:
        frm = t.get("last_success_state")
        to = t.get("first_failure_state")
        if frm not in STATE_INDEX or to not in STATE_INDEX:
            continue  # skip malformed
        m[STATE_INDEX[frm], STATE_INDEX[to]] += 1
    return m


def plot_heatmap(matrix: np.ndarray):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Reds",
        xticklabels=PIPELINE_STATES,
        yticklabels=PIPELINE_STATES,
        cbar_kws={"label": "Failure Count"},
        square=True,
    )
    # x-labels on TOP: this chart is read by COLUMN (first-failure), so the
    # column header should sit above the column you read down.
    ax.xaxis.set_label_position("top")
    ax.xaxis.tick_top()
    plt.title("Failure Transition Heatmap", fontsize=14, pad=40)
    plt.xlabel("First Failure State →")
    plt.ylabel("Last Success State ↓")
    plt.xticks(rotation=45, ha="left")
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=300)
    plt.close()
    print(f"Saved heatmap to {OUTPUT_PNG.relative_to(ROOT)}")


def plot_heatmap_with_margins(matrix: np.ndarray):
    """Heatmap + marginal totals.

    Column sums (bottom strip) = where failures FIRST land  -> the root-cause axis.
    Row sums    (right strip)  = where the agent was last healthy.
    The analysis hinges on the COLUMN totals (e.g. GetRecipes=32), which no single
    cell in the core grid makes visible. This view surfaces them directly.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    col_tot = matrix.sum(axis=0)  # first-failure totals (down each column)
    row_tot = matrix.sum(axis=1)  # last-success totals (across each row)

    fig = plt.figure(figsize=(12, 10))
    gs = fig.add_gridspec(
        2, 2, width_ratios=(20, 3), height_ratios=(20, 3),
        wspace=0.04, hspace=0.04,
    )
    ax = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1], sharey=ax)
    ax_bottom = fig.add_subplot(gs[1, 0], sharex=ax)

    sns.heatmap(
        matrix, annot=True, fmt="d", cmap="Reds",
        xticklabels=PIPELINE_STATES, yticklabels=PIPELINE_STATES,
        cbar=False, square=False, ax=ax,
    )
    ax.set_ylabel("Last Success State ↓")
    ax.set_title("Failure Transition Heatmap (with marginal totals)",
                 fontsize=14, pad=40)
    # x-labels on TOP of the grid (read each column down from its header);
    # the bottom column-sum strip keeps its own labels.
    ax.xaxis.set_label_position("top")
    ax.xaxis.tick_top()
    ax.tick_params(labelbottom=False, labeltop=True)
    ax.set_xlabel("First Failure State →")
    for lbl in ax.get_xticklabels():
        lbl.set_rotation(45)
        lbl.set_ha("left")

    # right strip: row totals (last-success)
    n = len(PIPELINE_STATES)
    y = np.arange(n) + 0.5
    ax_right.barh(y, row_tot, color="#9ecae1", height=0.9)
    ax_right.set_ylim(n, 0)
    for yi, v in zip(y, row_tot):
        if v:
            ax_right.text(v, yi, f" {v}", va="center", ha="left", fontsize=8)
    ax_right.set_xlabel("row Σ\n(last success)", fontsize=8)
    ax_right.tick_params(labelleft=False, left=False)
    ax_right.set_xticks([])
    for s in ("top", "right", "bottom"):
        ax_right.spines[s].set_visible(False)

    # bottom strip: column totals (first-failure) -> the headline axis
    x = np.arange(n) + 0.5
    bars = ax_bottom.bar(x, col_tot, color="#fb6a4a", width=0.9)
    # emphasize the max column
    if col_tot.max() > 0:
        bars[int(np.argmax(col_tot))].set_color("#a50f15")
    ax_bottom.set_xlim(0, n)
    for xi, v in zip(x, col_tot):
        if v:
            ax_bottom.text(xi, v, str(v), va="bottom", ha="center", fontsize=8)
    ax_bottom.set_xticks(x)
    ax_bottom.set_xticklabels(PIPELINE_STATES, rotation=45, ha="right")
    ax_bottom.set_ylabel("col Σ\n(first failure)", fontsize=8)
    ax_bottom.set_yticks([])
    ax_bottom.set_xlabel("First Failure State →")
    for s in ("top", "right", "left"):
        ax_bottom.spines[s].set_visible(False)

    fig.savefig(OUTPUT_PNG_MARGINS, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved heatmap to {OUTPUT_PNG_MARGINS.relative_to(ROOT)}")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> None:
    traces = load_labeled_traces()
    matrix = build_transition_matrix(traces)

    total = int(matrix.sum())
    print(f"Loaded {len(traces)} traces – total recorded failures: {total}\n")

    plot_heatmap(matrix)
    plot_heatmap_with_margins(matrix)

    # Simple textual summary
    if total:
        max_val = matrix.max()
        idx = np.argwhere(matrix == max_val)
        for i, j in idx:
            from_state = PIPELINE_STATES[i]
            to_state = PIPELINE_STATES[j]
            print(f"Most common: {from_state} → {to_state}  ({max_val} failures)")


if __name__ == "__main__":
    main() 