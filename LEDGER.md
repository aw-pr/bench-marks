# Task Ledger

Rolling index of all bench tasks. One row per task. Add a row when a scorecard is complete.

| Task ID | Date | Source | Summary | Winner | Scorecard |
|---------|------|--------|---------|--------|-----------|
| EXAMPLE-001 | 2026-05-15 | standalone | EXAMPLE — Gray-Scott reaction-diffusion step function in Python | claude | [scorecard](tasks/EXAMPLE-001/scorecard.md) |
| BENCH-001 | 2026-05-15 | standalone (AI-transformation-FS research sweep) | ~1500-word iTone post, open angle, persona-west-writing skill pasted in for fairness | codex (joint 29 with claude) | [scorecard](tasks/BENCH-001/scorecard.md) |
| BENCH-003 | 2026-05-21 | agentic-rag-kimble (pass-29) | Senior-engineer code review — two-tool comparison (claude + codex), cursor/gemini intentionally skipped | codex (30 vs 29) | [scorecard](tasks/BENCH-003/scorecard.md) |
| BENCH-004 | 2026-05-21 | agentic-rag-kimble (pass-29) | Senior-leader strategic review — two-tool comparison (claude + codex), cursor/gemini intentionally skipped | claude (30 vs 29) | [scorecard](tasks/BENCH-004/scorecard.md) |
| BENCH-005 | 2026-05-23 | fractals-from-the-90s (`feature/autometta` @ `bd5b84f`) | Orchestration meta-bench: U-FIX-4 Coordinator SSOT refactor under the autometta dispatch contract, Opus vs Codex CLI as orchestrator; both lanes escalated after 2 loops (Acceptance 20 and 18 FLAP), cursor/gemini skipped by design | claude (18 vs 13; audit trail, not Acceptance; codex lane uncommitted, scored from self-report) | [scorecard](tasks/BENCH-005/scorecard.md) |
| BENCH-006 | 2026-06-03 | fractals-from-the-90s (feat/julia-deep-zoom) | Tooling meta-bench: codegraph MCP vs grep/Read baseline (same model, Opus 4.8) — comprehension, index accuracy, orientation, capability | codegraph (rubric tie 27–27; codegraph-first, grep-verify) | [scorecard](tasks/BENCH-006/scorecard.md) |
| BENCH-007 | 2026-07-04 | standalone | Model-variant meta-bench: O(1) LFU cache kernel task across four frontier peer models (Fable, Opus, GPT-5.5, Gemini-Pro) — Opus **30/30** and Fable **30/30** complete; GPT-5.5 run 2026-10-10 and not yet scored, Gemini-Pro not run | tie so far (Fable 30 = Opus 30); rubric saturated on this task class | [scorecard](tasks/BENCH-007/scorecard.md) |
| BENCH-008 | 2026-08-23 | fractals-from-the-90s (`dev`) | Lever meta-bench, first `ab/` harness run: model tier Opus 5 vs Sonnet 5 over 2 task shapes, n=3, metered | **sonnet** (same 6/6 gate, −71.6% cost, −40% tool calls) | [scorecard](tasks/BENCH-008/scorecard.md) |
| BENCH-009 | 2026-10-10 | fractals-from-the-90s | Lever meta-bench, Codex tier: Terra vs Luna at medium effort over 4 tasks, n=5, run overnight, cost as share of the 5-hour window | **luna** (gate 18/20 vs 19/20, 45% less quota, 57% more output tokens) | [scorecard](tasks/BENCH-009/scorecard.md) |
