# The Bench

A personal model-evaluation harness for comparing four AI tools on identical tasks.

## Purpose

Subscription decisions are expensive guesses without data. The Bench turns a hunch ("Claude feels better at X") into a scored record. Each task brief is run independently through four tools, outputs are captured, and results are scored against a fixed rubric. The rolling dataset feeds the iTone Substack series — a first-person account of what the four subscriptions actually do differently, week by week.

## Tools under test

| Handle | Subscription | Notes |
|--------|-------------|-------|
| `claude` | Claude Max (Opus) | Orchestrator role for harness admin; also a subject under test |
| `codex` | Codex Plus | OpenAI Codex CLI in agent mode |
| `cursor` | Cursor Pro | IDE-integrated agent, Composer mode |
| `gemini` | Gemini Plus | Gemini CLI or AI Studio |

## Task-fork workflow

1. A self-contained task is identified in another repo or from scratch.
2. The task spec is copied here as `tasks/<id>/brief.md` — no code, just the brief.
3. Each tool is given the identical brief in isolation. No tool sees another tool's output.
4. Outputs are saved to `tasks/<id>/<tool>/` (or noted if the tool produced no artefact).
5. The scorecard is completed at `tasks/<id>/scorecard.md` using the rubric in `rubric.md`.
6. A row is added to `LEDGER.md`.

The brief must be self-contained: if it requires context from the source repo, that context is pasted into the brief, not linked. This keeps comparisons fair and reproducible.

## One-lead-model rule

Every project outside this repo keeps a single lead model on trunk. If a developer wants to trial an alternative tool on a task, they fork that task here. The comparison lives in bench-marks; the result (if useful) informs the source repo's lead-model choice. Cross-model collaboration on the same artefact is not permitted — it conflates authorship and makes scoring impossible.

See `MODELS.md` for the full policy.

## iTone Substack series

Results are written up as posts in the iTone series "What four AI subscriptions actually do". Each post covers one or more bench tasks, shares the scorecard, and draws a narrow, data-backed conclusion. The goal is specificity: not "Claude is better" but "on deterministic algorithmic tasks under 200 lines, Claude produced working code in one pass; Cursor required three correction cycles".

## Repo structure

```
bench-marks/
  rubric.md              Scoring dimensions and anchors
  MODELS.md              Lead-model policy
  LEDGER.md              Rolling index of all tasks
  START-PROMPT.md        Paste-ready orchestrator prompt for new tasks
  templates/
    brief-template.md    Task brief template
    scorecard-template.md Scorecard template
  tasks/
    <task-id>/
      brief.md           The task brief (identical input to all tools)
      scorecard.md       Scored results across all four tools
      claude/            Claude output artefacts (if any)
      codex/             Codex output artefacts (if any)
      cursor/            Cursor output artefacts (if any)
      gemini/            Gemini output artefacts (if any)
```
