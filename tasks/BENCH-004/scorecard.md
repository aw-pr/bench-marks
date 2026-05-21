# Scorecard — BENCH-004

> Scoring rubric and anchor definitions: see `rubric.md`.
> All scores are integers 1–5. Total is the sum of all six dimensions (max 30).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-004 |
| Date scored | 2026-05-21 |
| Scorer | orchestrator (Claude Opus 4.7) |
| Brief | [brief.md](./brief.md) |

---

## Tool provenance

| Tool row | Harness | Underlying model | Provider |
|----------|---------|------------------|----------|
| claude | Claude Code (native, Agent tool subagent) | Claude Sonnet 4.6 (`claude-sonnet-4-6`) — model override on the spawning Agent call | Anthropic |
| codex | Codex CLI (native, `codex exec --sandbox workspace-write`) | Codex GPT-5.3 (`gpt-5.3-codex`) — default per local `~/.codex/config.toml` | OpenAI |
| cursor | not run — see `cursor/NOT-RUN.md` | n/a | n/a |
| gemini | not run — see `gemini/NOT-RUN.md` | n/a | n/a |

**Tier match:** workhorse tier on both sides. Same pairing as BENCH-003, so cross-task comparison is fair.

---

## Results

| Tool | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|------|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| claude | 5 | 5 | 5 | 5 | 5 | 5 | **30** |
| codex | 5 | 5 | 4 | 5 | 5 | 5 | **29** |
| cursor | — | — | — | — | — | — | — |
| gemini | — | — | — | — | — | — | — |

---

## Per-tool notes

### Claude (Sonnet 4.6 via Agent tool)

Output at [`claude/output.md`](./claude/output.md). ~860 words. Verdict: *earns another 30 minutes; scale evidence is the gap*.

Strongest moves:
- Identified the `AlgorithmFamily` snowflake-outrigger sentence as "the strongest single sentence in the README for me" — a specific editorial callout that demonstrates the reviewer actually read the prose. Not a templated leader review.
- Praised the `docs/discussion.md` Gartner hedging ("press releases rather than independent surveys") explicitly as separating-this-from-the-Bustamante-obituary signal. That's a senior leader's reading — distinguishing *honest hedge* from *marketing*.
- Three ranked risks (laptop-scale evidence, schema-as-coupling-tax, vendor concentration) read as a leader's risks, not an engineer's — schema-as-coupling-tax at 140 engineers is the kind of operational question that does not surface in a code-level review.
- "Two engineers for a quarter to a viable internal pilot, assuming the ingest pattern generalises" — concrete adoption-cost framing.

Failure modes:
- None observed. Score 5 by default. The review correctly distinguished what it had verified (read the docs) from what it would need to verify (run the demo on enterprise-shaped data).

Quality score 5: voice is consistently first-person, the editorial choices are non-templated, and the "What would change my mind" closes with three specific, falsifiable asks.

### Codex (GPT-5.3 via `codex exec`)

Output at [`codex/output.md`](./codex/output.md). ~890 words. Verdict: *earns another 30 minutes; would not fund broad rollout yet*.

Strongest moves:
- Top-ranked risk = grounding reliability (sampled grounding 3.0 vs ≥3.5 target). This is the *correct* engineer-leader-bridging risk to elevate — it is the directly-measurable failure mode of the architecture at this snapshot. Claude ranked it lower and led with scale evidence; both are defensible, but for a leader with a live underperforming RAG project, grounding-fragility is arguably the more actionable framing.
- Caught the over-claim in README: *"hallucination requires fabricating a specific run ID"* (README line 52) — Codex correctly flagged this as directionally-true-but-overstated and pointed to README lines 151-152 where the project itself admits inflated counts and invented flow IDs were caught by the judge. This is a sharp internal-consistency catch the human reader would respect.
- "Adoption looks like a wedge" framing with three concrete sub-steps reads operationally sound.

Failure modes:
- None observed. Score 5 by default.

Quality score 4 (not 5): the review reads slightly more like a structured consultancy briefing than a leader's first-person voice. "Adoption looks like a wedge" works; "this is primarily complementary to existing flat-RAG vendor spend, not an immediate replacement" is the kind of sentence a senior leader would say *to a peer*, not write — phrased like a slide. The output meets the brief on every dimension but the persona signal is weaker than Claude's.

### Cursor / Gemini

Not run by design. See `cursor/NOT-RUN.md` and `gemini/NOT-RUN.md`.

---

## Verdict

**Winner:** claude (30 vs 29 — narrow margin)

**Runner-up:** codex

**Key finding (one sentence):**
On a senior-leader strategic review framed in first person, Claude Sonnet 4.6 hit a more credible persona register than Codex GPT-5.3 — same correctness on findings, same brief satisfied, but the editorial voice signal landed on the Anthropic side while Codex defaulted toward a structured-briefing register.

**iTone post angle (optional):**
Persona register is a measurable quality even when the conclusions match. For first-person leader-voice work (board memos, internal advisory writing, executive review), Claude held the register; for cross-file forensic code review (BENCH-003), Codex held the evidence density. Same workhorse tier, opposite strengths. The honest narrative is not "X is better" but "X is better at register, Y is better at audit" — and both are sometimes wrong about the same thing.
