#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["matplotlib>=3.9,<4"]
# ///
"""Render the README charts from the A/B medians.

Figures are written twice, light and dark, so the README can serve each via a
<picture> element. Every number below is transcribed from the named section of
ab/RESULTS.md; change it there first and re-run this.

    ./scripts/render-charts.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent.parent / "docs" / "img"

THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "ink": "#0b0b0b",
        "secondary": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "axis": "#c3c2b7",
        "opus": "#2a78d6",
        "sonnet": "#eb6834",
        "haiku": "#1baf7a",
    },
    "dark": {
        "surface": "#1a1a19",
        "ink": "#ffffff",
        "secondary": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "axis": "#383835",
        "opus": "#3987e5",
        "sonnet": "#d95926",
        "haiku": "#199e70",
    },
}

FONTS = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


def figure(theme, width, height):
    fig, ax = plt.subplots(figsize=(width, height), dpi=200)
    fig.patch.set_facecolor(theme["surface"])
    ax.set_facecolor(theme["surface"])
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(theme["axis"])
    ax.spines["left"].set_linewidth(1)
    ax.tick_params(length=0, colors=theme["muted"], labelsize=9)
    ax.xaxis.grid(True, color=theme["grid"], linewidth=1)
    ax.set_axisbelow(True)
    return fig, ax


def rounded_bar(ax, y, width, height, colour, radius_px=8):
    """A bar whose data end is rounded and whose baseline end is square.

    Both ends of a FancyBboxPatch round together, so the baseline end is drawn
    behind x=0 and cut off by the axis limit. The radius is given in pixels and
    converted here, because each chart has a different x scale and a radius in
    data units would round by a different visible amount on each. Call this only
    once the axis limits are final.
    """
    origin = ax.transData.transform((0, 0))
    px_per_x = ax.transData.transform((1, 0))[0] - origin[0]
    px_per_y = abs(ax.transData.transform((0, 1))[1] - origin[1])
    radius = radius_px / px_per_x
    patch = FancyBboxPatch(
        (-radius, y - height / 2),
        width + radius,
        height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=0,
        facecolor=colour,
        mutation_aspect=px_per_x / px_per_y,
        zorder=2,
    )
    ax.add_patch(patch)


def save(fig, ax, name, theme_name, theme, title, subtitle, title_pad=18):
    ax.set_title(
        title,
        loc="left",
        color=theme["ink"],
        fontsize=12.5,
        fontweight="600",
        pad=title_pad,
    )
    ax.text(
        0,
        1.02,
        subtitle,
        transform=ax.transAxes,
        color=theme["secondary"],
        fontsize=9,
        va="bottom",
    )
    fig.tight_layout()
    path = OUT / f"{name}-{theme_name}.png"
    fig.savefig(path, facecolor=theme["surface"], bbox_inches="tight", pad_inches=0.28)
    plt.close(fig)
    print(f"wrote {path.relative_to(OUT.parent.parent)}")


# ab/RESULTS.md -- "model_tier -- Opus 5 vs Sonnet 5": median USD per task, n=3.
TIER_COST = [("Opus 5", 0.3852), ("Sonnet 5", 0.1096)]

# ab/RESULTS.md -- "model_tier_haiku": gate passes out of 5 runs per task shape.
GATE = {
    "Narrative trace\n(follow a value through a call chain)": (5, 2),
    "Enumerative lookup\n(which callers touch X)": (5, 5),
}

# ab/RESULTS.md -- "repo_priming", the valid run. Percent change against control.
PRIMING = [
    ("Cache read tokens", 33.7),
    ("Cost (USD)", 20.8),
    ("Wall clock", 18.6),
    ("Tool calls", 9.1),
]
NOISE_FLOOR = 20.0


def chart_tier_cost(theme_name, theme):
    fig, ax = figure(theme, 7.2, 2.6)
    labels = [label for label, _ in TIER_COST]
    colours = [theme["opus"], theme["sonnet"]]
    ax.set_yticks(range(len(labels)), labels, color=theme["ink"], fontsize=10.5)
    ax.set_xlim(0, 0.46)
    ax.set_ylim(len(labels) - 0.45, -0.55)
    for i, (_, cost) in enumerate(TIER_COST):
        rounded_bar(ax, i, cost, 0.42, colours[i])
        ax.text(
            cost + 0.012,
            i,
            f"${cost:.4f}",
            va="center",
            color=theme["ink"],
            fontsize=10.5,
            fontweight="600",
        )
    ax.set_xlabel("median cost per task, USD", color=theme["muted"], fontsize=9)
    ax.text(
        0.1096 + 0.012,
        1.44,
        "71.6% cheaper, and it passed the same 6 of 6 answer-key gates",
        color=theme["secondary"],
        fontsize=9,
        va="center",
    )
    save(
        fig,
        ax,
        "tier-cost",
        theme_name,
        theme,
        "Routing cold repo comprehension down a tier",
        "bench-marks A/B, 12 cells (2 tasks x 2 arms x n=3), 2026-08-23",
    )


def chart_gate(theme_name, theme):
    fig, ax = figure(theme, 7.2, 3.0)
    shapes = list(GATE)
    arms = [("Sonnet 5", theme["sonnet"]), ("Haiku 4.5", theme["haiku"])]
    height = 0.34
    ax.set_yticks(range(len(shapes)), shapes, color=theme["ink"], fontsize=9.5)
    ax.set_xlim(0, 5.6)
    ax.set_xticks(range(6))
    ax.set_ylim(len(shapes) - 0.4, -0.6)
    for row, shape in enumerate(shapes):
        for arm, passes in enumerate(GATE[shape]):
            y = row + (arm - 0.5) * (height + 0.06)
            rounded_bar(ax, y, passes, height, arms[arm][1])
            ax.text(
                passes + 0.09,
                y,
                f"{passes}/5",
                va="center",
                color=theme["ink"],
                fontsize=10,
                fontweight="600",
            )
    ax.set_xlabel("runs passing the answer-key gate, out of 5", color=theme["muted"], fontsize=9)
    handles = [
        plt.Line2D([], [], marker="s", linestyle="none", markersize=9, color=colour)
        for _, colour in arms
    ]
    legend = ax.legend(
        handles,
        [name for name, _ in arms],
        loc="lower right",
        bbox_to_anchor=(1, 1.14),
        ncols=2,
        frameon=False,
        fontsize=9.5,
        handletextpad=0.5,
        columnspacing=1.4,
    )
    for text in legend.get_texts():
        text.set_color(theme["secondary"])
    save(
        fig,
        ax,
        "gate-by-shape",
        theme_name,
        theme,
        "One tier lower, the gate starts failing by task shape",
        "bench-marks A/B, 20 cells (2 tasks x 2 arms x n=5), 2026-09-18",
        title_pad=44,
    )


def chart_priming(theme_name, theme):
    fig, ax = figure(theme, 7.2, 3.0)
    labels = [label for label, _ in PRIMING]
    ax.set_yticks(range(len(labels)), labels, color=theme["ink"], fontsize=10.5)
    ax.set_xlim(0, 40)
    ax.set_ylim(len(labels) - 0.45, -0.95)
    ax.axvspan(0, NOISE_FLOOR, color=theme["grid"], zorder=0)
    ax.text(
        NOISE_FLOOR - 0.8,
        -0.72,
        "harness noise floor, +/-20%",
        color=theme["muted"],
        fontsize=8.5,
        ha="right",
        va="center",
    )
    for i, (_, delta) in enumerate(PRIMING):
        rounded_bar(ax, i, delta, 0.42, theme["opus"])
        ax.text(
            delta + 0.7,
            i,
            f"+{delta:.1f}%",
            va="center",
            color=theme["ink"],
            fontsize=10.5,
            fontweight="600",
        )
    ax.axvline(0, color=theme["axis"], linewidth=1)
    ax.set_xlabel(
        "change against the no-map control, higher is worse", color=theme["muted"], fontsize=9
    )
    save(
        fig,
        ax,
        "priming-delta",
        theme_name,
        theme,
        "The architecture map cost more and saved nothing",
        "bench-marks A/B, 20 cells (2 tasks x 2 arms x n=5), 2026-09-18",
    )


def main():
    plt.rcParams["font.family"] = FONTS
    OUT.mkdir(parents=True, exist_ok=True)
    for theme_name, theme in THEMES.items():
        chart_tier_cost(theme_name, theme)
        chart_gate(theme_name, theme)
        chart_priming(theme_name, theme)


if __name__ == "__main__":
    main()
