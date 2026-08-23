#!/usr/bin/env python3
"""Aggregate A/B run records into paired per-lever deltas.

Two rules drive the output:

1. Efficiency is compared only across runs that passed the answer-key gate.
   The cost of reaching a wrong answer is not a number worth averaging, and a
   lever that looks cheap because it fails fast is not a saving.

2. Deltas are paired per task, never a difference of grand means. An unusually
   expensive task landing more often in one arm would otherwise move the
   headline figure on its own.

Medians rather than means: n is small by design and one runaway run should not
carry the result.

Usage: analyse.py ab/runs/*.jsonl
"""
import json
import statistics
import sys
from collections import defaultdict

METRICS = [
    ("tool_calls", "tool calls", "{:.1f}"),
    ("num_turns", "turns", "{:.1f}"),
    ("total_cost_usd", "cost USD", "{:.4f}"),
    ("duration_ms", "wall ms", "{:.0f}"),
    ("output_tokens", "output tok", "{:.0f}"),
    ("cache_read_input_tokens", "cache read tok", "{:.0f}"),
]


def load(paths):
    rows = []
    for path in paths:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def pct(new, old):
    if old in (0, None) or new is None:
        return None
    return (new - old) / old * 100.0


def main(paths):
    rows = load(paths)
    if not rows:
        print("no run records found")
        return 1

    by_lever = defaultdict(list)
    for r in rows:
        by_lever[r["lever"]].append(r)

    for lever, lrows in sorted(by_lever.items()):
        print(f"\n{'=' * 72}\nLEVER: {lever}\n{'=' * 72}")

        # The gate, reported before any efficiency number, because a lever that
        # changes the failure rate has already answered the important question.
        print("\nGate (answer-key pass rate)")
        for arm in ("control", "treatment"):
            arms = [r for r in lrows if r["arm"] == arm]
            if not arms:
                continue
            passed = sum(1 for r in arms if r.get("passed"))
            missed = defaultdict(int)
            for r in arms:
                for term in r.get("missing_terms") or []:
                    missed[term] += 1
            note = ""
            if missed:
                note = "   most-missed: " + ", ".join(
                    f"{t}x{c}" for t, c in sorted(missed.items(), key=lambda kv: -kv[1])[:3])
            print(f"  {arm:<10} {passed}/{len(arms)} passed{note}")

        ok = [r for r in lrows if r.get("passed")]
        tasks = sorted({r["task"] for r in ok})
        if not tasks:
            print("\n  No run passed the gate. No efficiency comparison is meaningful.")
            continue

        print(f"\nPaired deltas over {len(tasks)} task(s) that passed in both arms"
              "  (treatment vs control, negative = treatment cheaper)")
        header = f"  {'metric':<16}{'control':>12}{'treatment':>12}{'delta':>12}{'delta %':>10}"
        print(header)
        print("  " + "-" * (len(header) - 2))

        for key, label, fmt in METRICS:
            c_meds, t_meds = [], []
            for task in tasks:
                c = [r[key] for r in ok if r["task"] == task and r["arm"] == "control" and r.get(key) is not None]
                t = [r[key] for r in ok if r["task"] == task and r["arm"] == "treatment" and r.get(key) is not None]
                if c and t:                       # paired: task must pass in BOTH arms
                    c_meds.append(statistics.median(c))
                    t_meds.append(statistics.median(t))
            if not c_meds:
                print(f"  {label:<16}{'—':>12}{'—':>12}{'—':>12}{'—':>10}   (no task passed in both arms)")
                continue
            cm, tm = statistics.median(c_meds), statistics.median(t_meds)
            d = tm - cm
            p = pct(tm, cm)
            print(f"  {label:<16}{fmt.format(cm):>12}{fmt.format(tm):>12}"
                  f"{fmt.format(d):>12}{(f'{p:+.1f}%' if p is not None else '—'):>10}")

        n_per_cell = min(
            len([r for r in ok if r["task"] == t and r["arm"] == a])
            for t in tasks for a in ("control", "treatment")
        ) if tasks else 0
        if n_per_cell < 3:
            print(f"\n  CAUTION: smallest cell has n={n_per_cell}. Below n=3 these deltas are"
                  "\n  descriptive only and must not be quoted as a result. This is the exact"
                  "\n  limitation BENCH-006 carried; do not repeat it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["ab/runs/model_tier.jsonl"]))
