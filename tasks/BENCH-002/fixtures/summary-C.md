# PLACEHOLDER — Summary C

This file is a placeholder. Populate it by running the Claude deep sweep and then:

```bash
python3 tasks/BENCH-002/scripts/scrub.py \
  --input /path/to/ai-regulation-fs-2026-claude-deep/summary-*.md \
  --provider claude \
  --stats /path/to/research-sweeper/runs/stats.json
```

The scrub script will assign the next available label and update `results/label-map.json`.
Delete this placeholder file before running the adjudicator.
