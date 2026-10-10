#!/usr/bin/env python3
"""
collate-results.py — de-anonymise adjudicator verdicts and join with token/cost data.

Usage:
    python3 collate-results.py \
        --verdicts  tasks/BENCH-002/results/verdicts-raw.json \
        --label-map tasks/BENCH-002/results/label-map.json \
        --stats     /path/to/research-sweeper/runs/stats.json \
        --out       tasks/BENCH-002/results/results-table.md

Writes a Markdown results table to --out.
"""

import argparse
import json
import sys
from pathlib import Path


SCORE_FIELDS = [
    "brief_coverage",
    "accuracy_grounding",
    "synthesis_depth",
    "fs_audience_usefulness",
    "prose_quality",
]

DIMENSION_LABELS = {
    "brief_coverage": "Coverage",
    "accuracy_grounding": "Accuracy",
    "synthesis_depth": "Synthesis",
    "fs_audience_usefulness": "FS Usefulness",
    "prose_quality": "Prose",
}


def load_json(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def find_run_stats(stats_data: list, provider: str) -> dict:
    """Most recent run entry for the given provider."""
    matching = [r for r in stats_data if r.get("provider") == provider]
    return matching[-1] if matching else {}


def format_cost(cost) -> str:
    if cost is None:
        return "n/a"
    return f"${cost:.4f}"


def format_tokens(tokens: dict) -> str:
    total_in = tokens.get("lanesIn", 0) + tokens.get("synthesisIn", 0)
    total_out = tokens.get("lanesOut", 0) + tokens.get("synthesisOut", 0)
    return f"{total_in:,} in / {total_out:,} out"


def collate(verdicts_path: str, label_map_path: str, stats_path: str, out_path: str) -> None:
    verdicts_list = load_json(verdicts_path)
    label_map = load_json(label_map_path)

    stats_data = []
    if stats_path:
        raw = load_json(stats_path)
        stats_data = raw if isinstance(raw, list) else raw.get("runs", [])

    # Index verdicts by label
    verdicts = {v["label"]: v for v in verdicts_list if "label" in v}

    rows = []
    for label in sorted(label_map.keys()):
        entry = label_map[label]
        provider = entry.get("provider", "unknown")
        verdict = verdicts.get(label, {})

        if "parse_error" in verdict:
            print(f"  Warning: verdict for label {label} had a parse error.", file=sys.stderr)

        scores = verdict.get("scores", {})
        notes = verdict.get("notes", {})

        # Pull run stats: prefer from label_map (captured at scrub time), fallback to stats.json
        run_stats = entry.get("run_stats") or find_run_stats(stats_data, provider)
        models = run_stats.get("models", {})
        tokens = run_stats.get("tokens", {})
        cost = run_stats.get("estimatedCostUSD")

        rows.append({
            "label": label,
            "provider": provider,
            "lane_model": models.get("lane", "n/a"),
            "synthesis_model": models.get("synthesis", "n/a"),
            "mode": run_stats.get("mode", "n/a"),
            "tokens": format_tokens(tokens) if tokens else "n/a",
            "cost": format_cost(cost),
            "scores": scores,
            "total": verdict.get("total", sum(scores.get(f, 0) for f in SCORE_FIELDS)),
            "notes": notes,
        })

    # Sort by total descending
    rows.sort(key=lambda r: r["total"], reverse=True)

    lines = [
        "# BENCH-002 Results — Research Sweep Quality",
        "",
        "## Summary scores",
        "",
        "| Provider | Label | " + " | ".join(DIMENSION_LABELS[f] for f in SCORE_FIELDS) + " | **Total** | Cost |",
        "|----------|-------|" + "|".join(["-" * (len(DIMENSION_LABELS[f]) + 2) for f in SCORE_FIELDS]) + "|-----------|------|",
    ]

    for r in rows:
        scores_str = " | ".join(str(r["scores"].get(f, "?")) for f in SCORE_FIELDS)
        lines.append(
            f"| {r['provider']} | {r['label']} | {scores_str} | **{r['total']}** | {r['cost']} |"
        )

    lines += [
        "",
        "## Run metadata",
        "",
        "| Provider | Mode | Lane model | Synthesis model | Tokens | Cost |",
        "|----------|------|-----------|-----------------|--------|------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['provider']} | {r['mode']} | {r['lane_model']} | {r['synthesis_model']} | {r['tokens']} | {r['cost']} |"
        )

    lines += ["", "## Adjudicator notes", ""]
    for r in rows:
        lines.append(f"### {r['provider']} (Label {r['label']})")
        lines.append("")
        overall = r["notes"].get("overall", "")
        if overall:
            lines.append(overall)
            lines.append("")
        for field in SCORE_FIELDS:
            note = r["notes"].get(field, "")
            if note:
                dim_label = DIMENSION_LABELS[field]
                score = r["scores"].get(field, "?")
                lines.append(f"- **{dim_label}** ({score}/5): {note}")
        lines.append("")

    out = "\n".join(lines)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(out, encoding="utf-8")
    print(f"Results table written to: {out_path}")

    # Print summary to stdout
    print("\nFinal scores:")
    for r in rows:
        print(f"  {r['provider']:8s} (label {r['label']}): {r['total']}/25 — {r['cost']}")


def main():
    parser = argparse.ArgumentParser(description="Collate adjudicator verdicts into a results table.")
    parser.add_argument("--verdicts", required=True, help="Path to results/verdicts-raw.json")
    parser.add_argument("--label-map", required=True, help="Path to results/label-map.json")
    parser.add_argument("--stats", default="", help="Path to research-sweeper runs/stats.json")
    parser.add_argument("--out", required=True, help="Output path for results-table.md")
    args = parser.parse_args()

    collate(args.verdicts, args.label_map, args.stats, args.out)


if __name__ == "__main__":
    main()
