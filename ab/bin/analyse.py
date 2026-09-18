#!/usr/bin/env python3
"""Aggregate A/B run records into paired per-lever deltas.

Two rules drive the output:

1. Efficiency is compared only across runs that passed the answer-key gate.
   The cost of reaching a wrong answer is not a number worth averaging, and a
   lever that looks cheap because it fails fast is not a saving.

2. Runs are aggregated per task before the arms are compared, so an unusually
   expensive task landing more often in one arm cannot move the headline on
   its own.

   Note what the headline row is and is not. It compares each ARM's median of
   per-task medians; it is not the median of per-task DELTAS. With a two-task
   corpus those differ sharply: the arm-level figure is dominated by whichever
   task is larger in absolute terms, so a lever that helps one task and not the
   other still reports a large headline. The per-task breakdown printed beneath
   each metric is the honest view, and is what the write-up should quote when
   the two tasks disagree.

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

        print(f"\nArm medians over {len(tasks)} task(s) that passed in both arms"
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
            if len(tasks) > 1:
                per = []
                for task, cmed, tmed in zip(tasks, c_meds, t_meds):
                    tp = pct(tmed, cmed)
                    per.append(f"{task.split('-')[0]} {tp:+.1f}%" if tp is not None else f"{task.split('-')[0]} —")
                spread = "  ".join(per)
                flag = ""
                sig = [pct(tm_, cm_) for cm_, tm_ in zip(c_meds, t_meds)]
                sig = [x for x in sig if x is not None]
                if len(sig) > 1 and (max(sig) > 0) != (min(sig) > 0):
                    flag = "   <- tasks DISAGREE in sign"
                print(f"  {'':<16}{'per task:':>12} {spread}{flag}")

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
