# Leader review — agentic-rag-kimble

**Verdict.** Yes, this earns another 30 minutes. The framing is sharper than most "RAG is dead" reactions I've read this quarter, the dimensional argument is genuinely load-bearing rather than decorative, and the eval numbers are reported honestly (including the misses). What stops me investing further today is scale evidence — 171k runs on a laptop with an MIT graph store I've not heard of in a board meeting is a long way from my 140-engineer corpus. I want the bridge.

## 1. Does the framing make sense?

Yes, and I could brief my CTO on it in two sentences: *flat chunk-based RAG cannot answer aggregate or join-shaped questions because vector similarity ranks by surface resemblance, not evidential usefulness; for dimensionally-shaped data, encode the schema into retrieval instead of asking the model to reconstruct it from prose.* That is exactly the gap I see in our internal "ask anything" tool — recall fine, aggregate answers shallow. The Kimball framing also lands because Kimball is a vocabulary my data org already speaks; "fact node, dimension node, conformed date" is not an extra concept tax. The snowflaked `AlgorithmFamily` outrigger justified explicitly as *"the kind of trade-off ... that flat-table RAG cannot express"* is the strongest single sentence in the README for me.

## 2. Blind alley?

Not obviously. The discussion doc earns credibility by **not** claiming RAG is dead — it stakes out structured RAG as one of three coexisting patterns ("flat", "structured", "long-context-only") and names where each fails. The long-context counter is engaged honestly: *"Anthropic removed its >200k-context surcharge in March 2026 ... The 'RAG saves tokens' argument weakens fast."* That is the right risk to flag. The Opus 4.6 MRCR figure (76% on 8-needle 1M-token) is cited as the best recent benchmark, not as a settled win. Vendor risk is real (LadybugDB is a Kùzu fork post-acqui-hire) but the architectural slot — schema-aware retrieval over dimensional data — outlives any specific store.

## 3. Investment thesis fit

Orthogonal, not replacement. My Glean-class contracts cover unstructured corpus retrieval (Confluence, Slack, Drive) where flat RAG is roughly adequate. This pattern is a *different bet* aimed at the structured-data questions Glean cannot answer — "which teams shipped most features", "what's our incident root-cause pattern" — which is precisely where I'm bleeding. At our scale the build looks like: pick a dimensional source (Jira+GitHub events, or PagerDuty+deploys), define the fact/dimension boundary, stand up one store. Two engineers for a quarter to a viable internal pilot, assuming the ingest pattern generalises. Not a Glean replacement; a sibling system behind the same chat surface.

## 4. Reader / runner experience

The README lands. Mermaid up top, honest eval table (pass-27 vs pass-28 with the misses called out), and the *"left visible rather than papered over"* note on the `HistGradientBoostingClassifier` failure is the kind of detail I trust. The discussion doc reads credibly — dated sources (Menlo Nov 2025, VentureBeat Retrieval Rebuild, Anthropic March 2026 pricing), Gartner figures explicitly flagged as *"press releases rather than independent surveys"*. That hedging is what separates this from the Bustamante obituary post I've seen forwarded around. Quick start is four commands. The 90-minute ingest is the friction point — I would not run that on a discovery call; a pre-baked smoke DB would change the answer.

## 5. Risks I'd raise (rank-ordered)

1. **Scale evidence is laptop-scale.** 171,250 runs on an M-series MacBook is a long way from enterprise corpus volumes. The discussion doc concedes this — *"single-writer embedded stores ... max out at the low hundreds of thousands of rows per minute"* — but does not show what the operational picture looks like at 50M or 500M fact rows. That's the volume my data lake is at. Until I see the tier-2 story (distributed graph, snapshot ingest), this is a pattern I'd pilot at department scale, not commit at company scale.
2. **Schema as a coupling tax.** *"Schema decisions are load-bearing, and adding a new data shape may require a model update rather than just re-embedding."* In a company where data shape changes faster than the platform team can ship, that is a real ops burden. Who owns the schema? What's the change-management process when a new dimension lands? The README does not have an answer because at one engineer it doesn't need one; at 140 engineers it's the question.
3. **Vendor concentration in the stack.** LadybugDB is a community fork of a database whose original maintainer was acqui-hired. The agent SDK is Anthropic-only. The embedding model is a single open-source checkpoint. None of these are fatal, but together they are three single points of failure for a system I'd be asked to defend in a procurement review.

## What would change my mind

1. **A reproduced eval against a non-toy enterprise-shaped corpus** — e.g. ingest a public Jira/GitHub events dataset, demonstrate the same lift on aggregate questions, show the recall ceiling holds. OpenML is a friendly corpus because it was Kimball-shaped to begin with.
2. **An operational section in the README.** What does on-call look like? What's the failure mode when ingest segfaults at 03:00 (the FU2 issue is named but not closed)? What's the per-query latency distribution under concurrent load? Right now the demo is sized for a laptop, not a duty rota.
3. **One paragraph on store portability.** If LadybugDB is hit by a bus tomorrow, what's the migration path — Neo4j, Memgraph, DuckDB-graph? The discussion doc names these as tier options but stops short of saying the schema is portable. Saying it explicitly would defuse the vendor-lock risk in five sentences.
