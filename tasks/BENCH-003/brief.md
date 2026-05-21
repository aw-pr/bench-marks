# Task Brief — BENCH-003

> Senior-engineer code review of the agentic-rag-kimble repository at pass-29.

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-003 |
| Date | 2026-05-21 |
| Source repo | agentic-rag-kimble (pass-29 branch) |
| Source issue / PR | n/a — review commissioned by repo owner |
| Tools to run | claude, codex *(cursor and gemini lanes intentionally skipped — see Notes for the scorer)* |

---

## Spec

Produce an independent senior-engineer review of `agentic-rag-kimble` covering five areas, in order:

1. **Does the method stack up?** Is the Kimball-on-property-graph approach sound, or is it cargo-culting? Where would it actually break?
2. **Code hygiene.** Spot-check `src/agent/orchestrator.py`, `src/retrieval/*`, `src/ingestion/openml_fetch_async.py`, `src/ingestion/transform.py`, the experiment scaffold under `src/experiment/`. Look for: type-hint consistency, error-handling gaps, untested critical paths, async footguns, secret leakage, dead code.
3. **Will it run from clone + brief config?** Walk the README Quick Start as if you cloned the repo today. What is missing or broken? Test coverage for the path from `pip install` to first query.
4. **Architecture.** Is the three-tool agent (graph / semantic / aggregate) the right shape? Is the in-process MCP server design wise? Does the ingestion pipeline have idempotency? Schema migration story?
5. **Operational concerns.** Observability, cost telemetry (`runs/cost-log.jsonl`), the publish-workflow guards, the autonomous experiment scaffold (`runs/experiment/`) — do these look load-bearing or pretend-load-bearing?

Read these documents as primary inputs: `README.md`, `docs/discussion.md`, `docs/architecture.md` if it exists, `docs/spec.md` if it exists, `CLAUDE.md`. Then dig into actual code under `src/` and `tests/unit/`. Cite specific `file:line` references for any concrete claim.

---

## Constraints

- Adopt the persona "Sam Cho" (claude lane) or "Morgan Reyes" (codex lane) — different names so output can be attributed without conflating providers.
- 15 years backend / data infra, has shipped 3 production RAG systems, currently evaluating retrieval architectures for an internal knowledge platform at a mid-sized SaaS company.
- Writes code reviews like a Stripe / Shopify reviewer: precise, no padding, willing to call out shortcuts directly.
- Sceptical of: clever abstractions that hide complexity, async sprawl, untested ingest pipelines, vendor lock-in via embeddings.
- Cite file:line for any concrete claim. "Couldn't verify" is an acceptable answer; vibes-based scoring is not.

---

## Definition of done

- [ ] One-sentence verdict at top (ship / hold / scrap-and-restart)
- [ ] Five sections matching the spec, each with a one-line verdict followed by 3–5 bullets of evidence
- [ ] A final "What I'd change first" section with three concrete next steps in priority order
- [ ] Length 800–1,200 words
- [ ] Every concrete claim carries a `file:line` citation or is explicitly hedged

---

## Context paste

The repository is at `~/repos/agentic-rag-kimble` on the `pass-29` branch. All documents listed in the spec exist there. Read them directly — do not synthesise content you have not read.

---

## Notes for the scorer

The cursor and gemini lanes were intentionally skipped for this round because the originating workflow (four-way review of agentic-rag-kimble) ran only the claude and codex pair, deliberately matching tiers across families per `[[reference_model_family_equivalents]]`. Cursor and Gemini outputs should be recorded as **not run** rather than void, with a note that this was a two-tool comparison by design.

Scoring this kind of review task against the standard rubric requires interpreting *Correctness* as "did the review surface real issues vs invent issues that don't exist", and *Failure mode* as "did the review caveat its hedges honestly". *Time to acceptable result* is the agent's wall-clock from dispatch to file written.
