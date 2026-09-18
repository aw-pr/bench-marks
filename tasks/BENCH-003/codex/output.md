**Hold.** The core retrieval shape is defensible, but the repo has enough contract drift, boundary handling gaps, and run-from-clone friction that I would not treat it as production-ready yet.

## 1) Method validity: Kimball-on-property-graph vs cargo cult
Verdict: **Sound for this data shape, but fragile at schema/data boundary and over-claimed in docs.**

- The data itself is naturally fact/dimension-like, and the implementation actually encodes that split (`Run` fact + dimensions + explicit edges), not just marketing language (`src/graph/schema.py:19-93`, `README.md:50-55`). This is not pure cargo cult.
- The retrieval split (graph query / semantic / aggregate) matches question classes and avoids forcing every question through vector similarity (`README.md:13-16`, `src/retrieval/graph_tool.py:36-53`, `src/retrieval/semantic_tool.py:15-53`, `src/retrieval/aggregate_tool.py:166-218`).
- Where it breaks first: semantic quality still depends on hand-synthesised short descriptions + optional OpenML text append, not robust canonical docs, so vocabulary miss remains a structural weakness (`src/ingestion/transform.py:186-223`, `src/ingestion/loader_async.py:199-203`, `README.md:137-138`).
- Where it breaks second: dimensional assumptions are brittle around null/partial measures; the code relies on permissive aggregate behavior rather than explicit data quality controls (`src/retrieval/aggregate_tool.py:97-102`, `src/retrieval/aggregate_tool.py:154-162`).
- Architecture/docs drift is material: architecture/spec still contain stale Kùzu/Chroma-era statements while claiming pass-21 updates, reducing trust in the design narrative (`docs/architecture.md:85-99`, `docs/spec.md:39-40`, `docs/spec.md:78-81`).

## 2) Code hygiene spot-check
Verdict: **Mixed. Strong unit-level discipline in pure logic; weak boundary hardening and some stale contracts.**

- Type hygiene is pragmatic but inconsistent at boundaries: many dynamic dict payloads and broad `Any` usage in orchestrator/tool plumbing, plus assert-based runtime guards that disappear under `-O` (`src/agent/orchestrator.py:20`, `src/agent/orchestrator.py:68-71`, `src/graph/db.py:92-101`).
- Error handling at critical boundaries is often swallow-and-continue without escalation path. Examples: write failures only logged in async writer, telemetry failures silently dropped, schema init runtime errors suppressed (`src/ingestion/loader_async.py:148-152`, `src/agent/orchestrator.py:250-255`, `src/graph/db.py:115-120`).
- Async footgun: module-level semaphore/cache state in `openml_fetch_async` is global mutable state; safe enough in single-process runs, risky for long-lived multi-run processes/tests without strict reset discipline (`src/ingestion/openml_fetch_async.py:45-59`, `src/ingestion/openml_fetch_async.py:61-76`).
- Secret handling looks clean in code (no API keys hardcoded, OAuth path documented), but UI still carries stale “inject credentials via 1Password” messaging that no longer matches runtime path (`CLAUDE.md:20-23`, `run-secure-query.sh:2-6`, `src/ui/app.py:277-279`, `src/ui/app.py:1067-1069`).
- Dead/stale contract indicators: `aggregate_tool` explicitly deviates from its own spec return type, and docs still reference obsolete components; this is acceptable short-term but should be reconciled or consumers will drift (`src/retrieval/aggregate_tool.py:7-13`, `docs/spec.md:84-90`).

## 3) Run-from-clone + quick start
Verdict: **Partially runnable, but quick-start path is inconsistent and underspecified.**

- README Quick Start uses async loader directly (`python -m src.ingestion.loader_async`), while repo’s ingestion script still calls sync loader (`scripts/ingest.sh` -> `src.ingestion.loader`) (`README.md:73-75`, `scripts/ingest.sh:40-41`). That is an avoidable operator split.
- Quick Start requires heavy local preconditions (LadybugDB extension behavior, model downloads, Claude Code authenticated session) but does not provide an explicit “preflight” command to validate them before a 90-minute ingest (`README.md:73-90`, `src/graph/db.py:47-56`, `src/agent/orchestrator.py:152-155`).
- Unit coverage is broad for transforms/tools/async fetch/tick state machines, but there is no clone-to-first-query integration test path covering install → ingest sample → build index → query (`tests/unit/test_transform.py`, `tests/unit/test_async_fetch.py`, `tests/unit/test_orchestrator.py`). Couldn’t verify end-to-end pass without running.
- `smoke-test.sh` is useful but not a true smoke for onboarding: it assumes lint/mypy/pytest env and includes eval tests, not a minimum runnable path for a new clone (`scripts/smoke-test.sh:7-21`).
- README claims about green gates and counts may be true, but without CI artifacts in the repo they are “trust me” statements; couldn’t verify from static read alone (`README.md:185-187`).

## 4) Architecture choices
Verdict: **Three-tool agent shape is right; in-process MCP is fine for local, but ingestion/schema lifecycle is underpowered for evolution.**

- Three-tool split is the correct minimum interface and avoids abstraction sprawl; tools are explicit and constrained (`src/agent/orchestrator.py:163-168`, `src/retrieval/tools.py:40-47`).
- In-process MCP server per query is acceptable for a local single-user demo, but it rebuilds the tool server each call and keeps shared config in a module-global, which is not concurrency-safe for future multi-request execution (`src/agent/orchestrator.py:64-66`, `src/agent/orchestrator.py:160-168`).
- Idempotency in ingestion is real but mostly in-memory reservation-set based; this works for single-process runs, not robust against crashes between reservation and durable write (potential partial-state behavior) (`src/ingestion/loader_async.py:20-25`, `src/ingestion/loader_async.py:182-196`, `src/ingestion/loader_async.py:312-323`).
- Schema migration story is effectively “reset schema” or opportunistic `IF NOT EXISTS` creation, not versioned migrations. That is fine for experimentation, weak for long-lived environments (`src/graph/schema.py:127-155`, `src/graph/db.py:122-127`).
- There is explicit acknowledgement of write-serialization and single writer, which is honest and technically coherent (`src/ingestion/loader_async.py:10-18`, `src/ingestion/loader_async.py:140-152`).

## 5) Operational concerns
Verdict: **Some load-bearing pieces exist, but observability/cost/publish/experiment scaffolding are uneven.**

- Cost telemetry is real and append-only (`runs/cost-log.jsonl` writer + model usage), but failures are swallowed and there is no durability/rotation/validation policy (`src/agent/cost_log.py:35-57`, `src/agent/orchestrator.py:250-255`).
- Observability for ingestion is mainly logs and counters; no explicit failure budget, retry taxonomy, or structured error stream beyond warnings (`src/ingestion/loader_async.py:126-135`, `src/ingestion/loader_async.py:148-152`).
- Publish workflow guardrails look substantial, not fake: fail-closed pre-push model, local config-based remote matching, install script idempotency (`docs/PUBLISH-WORKFLOW.md:95-107`, `scripts/install-guards.sh:13-20`, `scripts/install-guards.sh:49-63`).
- Experiment scaffold is more than vibes: explicit state machine, retries, stall detection, verifier loop, commit integration, and strong unit coverage (`src/experiment/tick.py:86-297`, `tests/unit/experiment/test_tick.py:83-149`, `tests/unit/experiment/test_tick.py:199-273`).
- But the scaffold’s own commit module documents a provenance hazard under parallel workers (`git add -A` cross-task bleed), which is a real operational risk if defaults change (`src/experiment/commit.py:15-21`).

## What I'd change first
1. **Unify and harden the onboarding path.** Make one canonical ingest command (async), update `scripts/ingest.sh` to match README, add a `scripts/preflight.sh` that checks Claude auth session, Ladybug VECTOR extension, writable paths, and small sample query path before full ingest.
2. **Close contract drift and boundary gaps.** Reconcile `docs/spec.md`/`docs/architecture.md` with current code, remove stale 1Password UI guidance, and replace assert-based runtime invariants + silent `except Exception: pass` at critical boundaries with typed errors and explicit failure reporting.
3. **Introduce minimal migration and resilience controls.** Add schema versioning metadata + forward migration scripts, make ingestion writes auditable with structured event logs, and gate idempotency claims with crash-recovery tests on async ingestion (reservation vs durable write behavior).
