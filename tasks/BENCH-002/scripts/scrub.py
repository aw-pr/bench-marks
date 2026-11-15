#!/usr/bin/env python3
"""
scrub.py — strip provider-identifying content from research-sweeper summary outputs
and write blind-labelled fixtures for BENCH-002.

Usage (single file):
    python3 scrub.py --input /path/to/summary.md --provider gemini --stats /path/to/stats.json

Usage (batch, all three providers at once):
    python3 scrub.py --batch \
        --gemini  /path/to/gemini/summary-*.md \
        --openai  /path/to/openai/summary-*.md \
        --claude  /path/to/claude/summary-*.md \
        --stats   /path/to/research-sweeper/runs/stats.json \
        --out-dir tasks/BENCH-002/fixtures

The script writes:
  fixtures/summary-A.md, summary-B.md, summary-C.md   (scrubbed, blind-labelled)
  fixtures/scrub-manifest.json                         (what was removed per fixture)
  results/label-map.json                               (GITIGNORED — maps A/B/C to provider)

Label assignment is randomised on first run and frozen thereafter. Re-running is a no-op
unless --force is passed.
"""

import argparse
import glob
import json
import os
import random
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Provider markers to scrub from body text.
# Conservative: replaces proper names only. Model-specific capability language
# (e.g. "Gemini Deep Think") is intentionally left in — the adjudicator must
# score on content quality, and capability references are expected in a sweep
# about frontier AI. Only the explicit provider attribution is stripped.
# ---------------------------------------------------------------------------
PROVIDER_NAMES = [
    # Order matters: longer/more-specific strings first to avoid partial matches.
    "Google DeepMind",
    "Anthropic",
    "OpenAI",
    "Gemini",
    "Claude",
    "GPT",
]

REPLACEMENT = "[MODEL-PROVIDER]"

# YAML frontmatter fields that identify the provider or model.
FRONTMATTER_SCRUB_FIELDS = {
    "provider",
    "model_lane",
    "model_synthesis",
    "brief_file",
    "tags",
}

# Regex patterns for content blocks to remove entirely (not just replace).
# These are structural elements, not text replacements.
REMOVE_PATTERNS = [
    # Obsidian transclusion link at end of summary: ![[sources-...]]
    re.compile(r"^!\[\[sources-[^\]]+\]\]\s*$", re.MULTILINE),
    # Vertex AI Search redirect URLs (Gemini-specific grounding redirects)
    re.compile(
        r"https://vertexaisearch\.cloud\.google\.com/grounding-api-redirect/[A-Za-z0-9_\-=]+",
        re.IGNORECASE,
    ),
    # Inline source citation links in the format: [[sources-slug#^id|Outlet (Year)]] ([↗](URL))
    # We keep the outlet/year text but strip the Obsidian wikilink wrapper and URL.
    re.compile(
        r"\[\[sources-[^\]]+\]\]\s*\(\[↗\]\([^)]+\)\)",
        re.IGNORECASE,
    ),
]


def _scrub_frontmatter(text: str) -> tuple[str, dict]:
    """
    Strip provider-identifying fields from YAML frontmatter (--- delimited block).
    Returns (scrubbed_text, manifest_of_removed_fields).
    """
    removed = {}
    if not text.startswith("---"):
        return text, removed

    end = text.find("\n---", 3)
    if end == -1:
        return text, removed

    frontmatter_block = text[3:end]
    body = text[end + 4:]  # skip the closing ---\n

    new_lines = []
    for line in frontmatter_block.splitlines():
        field = line.split(":")[0].strip().lstrip("-").strip()
        if field in FRONTMATTER_SCRUB_FIELDS:
            removed[field] = line.strip()
        else:
            new_lines.append(line)

    scrubbed_fm = "---\n" + "\n".join(new_lines) + "\n---"
    return scrubbed_fm + body, removed


def _scrub_provider_names(text: str) -> tuple[str, list[str]]:
    """
    Replace provider/model company names with [MODEL-PROVIDER].
    Returns (scrubbed_text, list_of_replacements_made).
    """
    replacements = []
    for name in PROVIDER_NAMES:
        pattern = re.compile(re.escape(name), re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            replacements.extend(matches)
            text = pattern.sub(REPLACEMENT, text)
    return text, replacements


def _remove_structural_patterns(text: str) -> tuple[str, list[str]]:
    """
    Remove structural blocks (transclusions, redirect URLs, citation wikilinks).
    Returns (scrubbed_text, list_of_removed_strings).
    """
    removed = []
    for pattern in REMOVE_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            removed.extend(matches if isinstance(matches[0], str) else [str(m) for m in matches])
        text = pattern.sub("", text)
    return text, removed


def scrub_file(input_path: str) -> tuple[str, dict]:
    """
    Read a summary file, apply all scrubbing passes, and return
    (scrubbed_content, manifest_dict).
    """
    raw = Path(input_path).read_text(encoding="utf-8")

    text, fm_removed = _scrub_frontmatter(raw)
    text, name_replacements = _scrub_provider_names(text)
    text, structural_removed = _remove_structural_patterns(text)

    # Clean up any double-blank lines left by removals.
    text = re.sub(r"\n{3,}", "\n\n", text)

    manifest = {
        "source_file": str(input_path),
        "frontmatter_fields_removed": fm_removed,
        "provider_name_replacements": list(set(name_replacements)),
        "structural_blocks_removed_count": len(structural_removed),
    }
    return text.strip(), manifest


def _find_run_stats(stats_path: str, provider: str) -> dict:
    """
    Pull the most recent run entry for the given provider from stats.json.
    Returns a dict with runId, models, tokens, estimatedCostUSD.
    """
    if not stats_path or not os.path.exists(stats_path):
        return {}
    try:
        data = json.loads(Path(stats_path).read_text(encoding="utf-8"))
        runs = data if isinstance(data, list) else data.get("runs", [])
        # Most recent run for this provider (last entry wins)
        matching = [r for r in runs if r.get("provider") == provider]
        if not matching:
            return {}
        run = matching[-1]
        return {
            "runId": run.get("runId"),
            "mode": run.get("mode"),
            "models": run.get("models", {}),
            "tokens": run.get("tokens", {}),
            "estimatedCostUSD": run.get("estimatedCostUSD"),
        }
    except Exception as e:
        print(f"  Warning: could not read stats for {provider}: {e}", file=sys.stderr)
        return {}


def write_single(input_path: str, provider: str, label: str, out_dir: str, stats_path: str = "") -> dict:
    """Scrub one file and write it to out_dir/summary-{label}.md."""
    os.makedirs(out_dir, exist_ok=True)
    scrubbed, manifest = scrub_file(input_path)
    out_path = os.path.join(out_dir, f"summary-{label}.md")
    Path(out_path).write_text(scrubbed, encoding="utf-8")
    manifest["label"] = label
    manifest["provider"] = provider
    manifest["output_file"] = out_path
    run_stats = _find_run_stats(stats_path, provider)
    return {**manifest, "run_stats": run_stats}


def _assign_labels(providers: list[str]) -> dict[str, str]:
    """Randomly assign A/B/C labels to providers."""
    labels = ["A", "B", "C"]
    random.shuffle(labels)
    return {p: l for p, l in zip(providers, labels)}


def run_batch(args) -> None:
    """Scrub all three providers and write fixtures + manifest + label map."""
    fixtures_dir = os.path.join(args.out_dir)
    results_dir = os.path.join(os.path.dirname(args.out_dir), "results")
    label_map_path = os.path.join(results_dir, "label-map.json")
    manifest_path = os.path.join(fixtures_dir, "scrub-manifest.json")

    os.makedirs(fixtures_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # Freeze label assignment if already exists and --force not set.
    if os.path.exists(label_map_path) and not getattr(args, "force", False):
        existing = json.loads(Path(label_map_path).read_text())
        label_map = {entry["provider"]: entry["label"] for entry in existing.values()}
        print(f"  Label map already exists at {label_map_path}. Using existing assignment.")
        print(f"  Pass --force to re-randomise. Current mapping: {label_map}")
    else:
        providers_present = []
        for p in ["gemini", "openai", "claude"]:
            if getattr(args, p, None):
                providers_present.append(p)
        label_map = _assign_labels(providers_present)
        print(f"  Assigned labels: {label_map}")

    manifests = []
    label_map_full = {}

    for provider in ["gemini", "openai", "claude"]:
        input_glob = getattr(args, provider, None)
        if not input_glob:
            print(f"  Skipping {provider} (no --{provider} argument)")
            continue
        # Resolve glob
        matches = glob.glob(input_glob)
        if not matches:
            print(f"  Warning: no files matched for --{provider} {input_glob}")
            continue
        input_path = matches[0]
        label = label_map[provider]
        m = write_single(input_path, provider, label, fixtures_dir, args.stats)
        manifests.append(m)
        label_map_full[label] = {
            "label": label,
            "provider": provider,
            "source_file": input_path,
            "run_stats": m.get("run_stats", {}),
        }
        print(f"  {provider} -> {label}: {m['output_file']}")

    Path(manifest_path).write_text(json.dumps(manifests, indent=2), encoding="utf-8")
    Path(label_map_path).write_text(json.dumps(label_map_full, indent=2), encoding="utf-8")
    print(f"\n  Manifest written: {manifest_path}")
    print(f"  Label map written (GITIGNORED): {label_map_path}")


def run_single(args) -> None:
    """Single-file mode: scrub one file and print manifest to stdout."""
    # Determine next available label
    fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures")
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    label_map_path = os.path.join(results_dir, "label-map.json")

    existing_labels = set()
    if os.path.exists(label_map_path):
        existing = json.loads(Path(label_map_path).read_text())
        existing_labels = {v["label"] for v in existing.values()}

    available = [l for l in ["A", "B", "C"] if l not in existing_labels]
    if not available:
        print("Error: all three labels (A, B, C) already assigned. Use --batch or --force.", file=sys.stderr)
        sys.exit(1)

    label = available[0]
    m = write_single(args.input, args.provider, label, fixtures_dir, args.stats)

    # Update label map
    os.makedirs(results_dir, exist_ok=True)
    label_map = {}
    if os.path.exists(label_map_path):
        label_map = json.loads(Path(label_map_path).read_text())
    label_map[label] = {
        "label": label,
        "provider": args.provider,
        "source_file": args.input,
        "run_stats": m.get("run_stats", {}),
    }
    Path(label_map_path).write_text(json.dumps(label_map, indent=2), encoding="utf-8")

    print(json.dumps(m, indent=2))
    print(f"\nWrote {m['output_file']} (label {label})")
    print(f"Updated label map: {label_map_path}")


def main():
    parser = argparse.ArgumentParser(description="Scrub research-sweeper summaries for blind adjudication.")
    parser.add_argument("--batch", action="store_true", help="Batch mode: scrub all three providers at once.")
    parser.add_argument("--input", help="Single-file mode: path to summary file.")
    parser.add_argument("--provider", choices=["gemini", "openai", "claude"], help="Provider for --input.")
    parser.add_argument("--gemini", help="Batch: glob/path to Gemini summary file.")
    parser.add_argument("--openai", help="Batch: glob/path to OpenAI summary file.")
    parser.add_argument("--claude", help="Batch: glob/path to Claude summary file.")
    parser.add_argument("--stats", default="", help="Path to research-sweeper runs/stats.json.")
    parser.add_argument(
        "--out-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "fixtures"),
        help="Output directory for fixtures (default: tasks/BENCH-002/fixtures).",
    )
    parser.add_argument("--force", action="store_true", help="Re-randomise label assignment even if map exists.")

    args = parser.parse_args()

    if args.batch:
        run_batch(args)
    elif args.input and args.provider:
        run_single(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
