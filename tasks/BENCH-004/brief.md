# Task Brief — BENCH-004

> Senior-leader strategic review of the agentic-rag-kimble repository at pass-29.

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-004 |
| Date | 2026-05-21 |
| Source repo | agentic-rag-kimble (pass-29 branch) |
| Source issue / PR | n/a — review commissioned by repo owner |
| Tools to run | claude, codex *(cursor and gemini lanes intentionally skipped — see Notes for the scorer)* |

---

## Spec

Produce an independent senior-leader review of `agentic-rag-kimble` covering five areas, in order:

1. **Does the framing make sense to a leader who reads this material?** Is the bet (Kimball-on-graph for dimensional data) defensible and clearly stated? Could the reviewer re-explain it to their CTO / board?
2. **Is this a blind alley?** Is the direction about to be obsoleted by long-context or a vendor product, or does it sit in a stable architectural slot?
3. **How does this square with the reviewer's current investment thesis?** They have flat-RAG vendor contracts active. Does this approach complement, replace, or sit orthogonal to those? What would adoption look like at their org's scale?
4. **The experience as a reader / part-time runner of the harness.** Do the README and `docs/discussion.md` land? Is the discussion doc credible (sources, dates, hedges) or marketing? If the reviewer ran one query, would they continue?
5. **Risks they would raise to a peer thinking of investing time here.** Three concrete risks, rank-ordered.

Read primarily: `README.md`, `docs/discussion.md`. Glance at `docs/architecture.md` and `docs/spec.md` if they exist.

---

## Constraints

- Adopt the persona "Alex Quinn" (claude lane) or "Jordan Patel" (codex lane).
- VP Engineering at a mid-market enterprise (~$400M revenue, ~900 employees, ~140 engineers). 20 years technology leadership, hands-on background kept warm.
- Current AI tooling spend: $1–3M/year (ChatGPT Enterprise, Claude Team, Glean-class vendor RAG, embedding API budget).
- Has live RAG project that has been underperforming for two quarters — recall fine, aggregate answers shallow.
- Reads Latent Space, Stratechery, a16z; has read Bustamante's "RAG Obituary".
- Time-poor — would skim the README, glance at the discussion doc, maybe spin up the demo for ten minutes.
- Sceptical of: developer-toy projects that don't generalise; "RAG is dead" hot takes without independent evidence; architectural perfection without operational reality; premature vendor lock-in.

---

## Definition of done

- [ ] One-paragraph verdict at top, ≤80 words, answering "does this earn another 30 minutes of my time?"
- [ ] Five sections matching the spec
- [ ] A final "What would change my mind" section with 2–3 specific things the project could do to win the reviewer over
- [ ] Length 600–900 words
- [ ] First-person voice as the persona
- [ ] Verbatim short quotes from the docs where they are load-bearing

---

## Context paste

The repository is `agentic-rag-kimble` on the `pass-29` branch (the orchestrator passes the working-tree path at dispatch time). Documents listed in the spec exist there.

---

## Notes for the scorer

Same as BENCH-003: cursor and gemini lanes intentionally skipped — this was a two-tool comparison by design.

For a leader review, *Correctness* maps to "did the review identify real strategic risks vs invent generic ones", *Quality* to "does it read like a senior leader's voice (not a consultancy template)", and *Failure mode* to "did the review hedge its market claims honestly".
