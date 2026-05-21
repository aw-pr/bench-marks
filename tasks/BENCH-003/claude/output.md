# Engineer review — agentic-rag-kimble

**Verdict: ship as a portfolio / demo artefact; hold before treating it as a template for a 5 PB internal platform.** The core idea is honest and the code is above hobby grade, but several boundaries (auth, ingestion runner, schema-on-graph drift) are not where you'd want them at SaaS scale.

---

## 1. Does the method stack up?

**Verdict: sound for this corpus shape, oversold as a general pattern.**

- Kimball-on-graph is a real fit for OpenML. `Run` genuinely is a fact (immutable, measured, dated) and `Algorithm/Dataset/Task` genuinely are conformed dimensions. `docs/architecture.md:36-44` correctly maps fact/dim/measure and uses tool selection rather than always-vector — that part is not cargo-culting.
- The snowflake `AlgorithmFamily` outrigger (`README.md:54`, `src/retrieval/aggregate_tool.py:94-95`) is the kind of move you only make if you've actually done dimensional modelling; nine hand-curated families in `src/ingestion/family_metadata.py` is a load-bearing taxonomy, not a join you can derive at query time.
- Where it breaks: the schema is **closed-world**. New algorithm families need a code change (`src/ingestion/transform.py:18-40` is a hard-coded substring rule list). For a 5 PB heterogeneous corpus where you don't know the entity types in advance, this is the wrong shape — the dimensional commitment that helps here would be the thing that kills you at scale, exactly as `docs/discussion.md:24-31` admits.
- The "structurally harder to hallucinate" claim (`docs/architecture.md:215-217`) is overstated. Grounding rule lift was 2.4 → 3.0 / 5.0 (`README.md:155`), still short of the 3.5 target. Structure helps; it does not eliminate the model inventing flow IDs (called out honestly in the README).
- The corpus is 171k runs (`README.md:89`), not "18M". The headline number in the front-matter is the upstream OpenML total, not what's loaded. Marketing-grade truth; the body of the README catches itself, which is fine.

## 2. Code hygiene

**Verdict: pragmatic, with two real footguns and one whiff of dead code.**

- **Global mutable state in the orchestrator.** `src/agent/orchestrator.py:65,160-161` parks the `Config` on a module-level `_current_config` and reads it inside the `@tool` callbacks via `_require_config()`. This is fine for the single-shot CLI invocation, but `run_query` doing `asyncio.run(...)` (line 155) plus a global makes it non-reentrant from any async caller and unsafe if the Streamlit app ever services two queries concurrently. Pass the config via a `contextvars.ContextVar` or a closure factory.
- **Best-effort cost log swallows everything.** `src/agent/orchestrator.py:251-255` wraps the cost-log write in a bare `except Exception: pass`. The docstring on `src/agent/cost_log.py:20-22` says it swallows "an OSError"; the actual code swallows *anything*, including programmer errors in the log_response shape. Either log to stderr or narrow the except.
- **Two parallel write-guards.** `src/graph/db.py:23-26` and `src/retrieval/graph_tool.py:16-19` both regex for write keywords. They are subtly different (`REMOVE` is only in graph_tool). Same rule, two enforcement points — pick one. The DB-level one is the security boundary; the tool-level one is duplicate defence that will silently drift.
- **Dead-code suspects.** `src/agent/prompts.py` is 54 lines but `extract_citations` (`orchestrator.py:140-142`) is the only consumer of the citation contract; the SDK switch deprecated `src/retrieval/tools.py:get_tool_schemas` and the per-tool `*_tool_schema()` helpers (`graph_tool.py:56`, `aggregate_tool.py:221`, `semantic_tool.py:55`) — only `dispatch_tool` is wired through the SDK. The schemas are now duplicated in the `@tool` decorator. `run-secure-query.sh` self-admits to being vestigial (`CLAUDE.md`).
- **Type hygiene.** `transform.py` is genuinely well-typed and pure as advertised; `_safe_float`'s `f != f` NaN trick (line 301) is fine. Async fetch (`openml_fetch_async.py`) has a single shared module-level semaphore and dict caches (`_flow_cache`, `_dataset_desc_cache`) — fine for single-process ingest, would race if you ever ran two ingests in one interpreter. Not currently a footgun, but worth a comment.
- **Async footgun, minor.** `openml_fetch_async.py:165-172` does broad `except (KeyError, ValueError, TypeError): continue` over evaluation rows. With OpenML's flakiness that's defensible, but you'll never know what you dropped. Add a counter.

## 3. Will it run from clone + brief config?

**Verdict: no — the Quick Start is two commands short.**

- `README.md:74` says `python -m src.ingestion.loader_async --max-datasets 500 ...`. That works (`loader_async.py:546` has a `__main__`). Good.
- `README.md:77` says `./scripts/build-index.sh`. That exists and looks idempotent. Good.
- **Missing:** there is no `db.initialise_schema()` step between install and ingest. `scripts/ingest.sh` does it (`scripts/ingest.sh:23-31`) but the README does not invoke `ingest.sh`; it invokes `loader_async` directly. A fresh clone needs to either run `./scripts/ingest.sh --dry-run` first or have the loader call `initialise_schema()` itself. Worth verifying with a docker-clean run.
- **Auth surprise.** `README.md:83` claims OAuth "is handled automatically by the Claude Agent SDK via the Claude Code session." True if the operator has Claude Code installed and logged in; not true otherwise. There is no precondition check or friendly error — `orchestrator.py` will just raise out of the SDK. A `--check-auth` smoke command would close this.
- **`pyproject.toml` build backend looks wrong.** `pyproject.toml:3` has `build-backend = "setuptools.backends.legacy:build"`. The standard value is `setuptools.build_meta`. `pip install -r requirements.txt` won't trip on this because the project isn't installed as a package, but `pip install -e .` would. Whether that matters depends on intent.
- **Tests don't gate the README.** `scripts/smoke-test.sh:17` runs `pytest tests/eval/`, which exists (`runs/` listing) — `tests/eval/test_end_to_end.py` and `test_fixtures_coverage.py`. But the eval suite is DB-dependent; a fresh clone with no `data/kuzu_db/` will fail smoke-test at that step. The unit suite (5,383 lines, 420 tests claimed) is the actually-runnable-from-clone target; advertise that separately.

## 4. Architecture

**Verdict: the three-tool shape is right; the in-process MCP server is a clever-but-fragile choice.**

- Three tools (graph / semantic / aggregate) is the correct decomposition. Aggregate is the one that earns its keep — flat RAG genuinely cannot do `aggregate_measures(group_by="algorithm_family.paradigm", measure="accuracy")` (`aggregate_tool.py:81-163`). The Cypher is built server-side from a whitelist (`VALID_GROUP_BY`, line 40), which is the right injection posture.
- **In-process MCP server** (`orchestrator.py:164-168` via `create_sdk_mcp_server`) is a real innovation over hand-rolled SDK tool loops, but it ties you to `claude-agent-sdk`'s lifecycle. The `_current_config` module-level shim (above) is what that design coupling looks like in practice — there's no clean place to thread per-call state through `@tool`-decorated coroutines.
- **Idempotency is shallow.** `loader_async.py:108-120` keeps `IngestState` with pre-loaded PK sets and an `asyncio.Lock`. Re-running pulls the existing PKs into Python memory and skips. That works for "I crashed halfway through the same scope" but **does not handle property drift** — if `transform_algorithm` produces a different `family` for the same `flow_id` in a later pass (which happens when the rules in `transform.py:18-40` change), the existing node is *not* updated. Pass 28's "OpenML free-form description backfill" required a separate backfill script (`scripts/backfill-openml-descriptions.sh`) precisely because of this. There is no `MERGE`-on-update path.
- **Schema migration story is informal.** `src/graph/schema.py` (174 lines) just drops and recreates. Pass-over-pass changes are tracked by `runs/build-log/pass-N-*.md` retros and ad-hoc `scripts/backfill-*.sh`. Workable for a solo build log; would not survive multi-engineer ownership.
- **No vendor lock-in via embeddings, which is rare and good.** `BAAI/bge-small-en-v1.5` is a local 130MB model (`src/retrieval/embedder.py`), so embeddings are reproducible and the index can be rebuilt deterministically. Don't underrate this — it's the single biggest hygiene win over OpenAI-embedded RAG repos.

## 5. Operational concerns

**Verdict: cost telemetry is real; observability is thin; the experiment scaffold is impressively engineered but doing more than it needs to.**

- `runs/cost-log.jsonl` is **load-bearing** — `src/agent/cost_log.py` writes one line per query with usage, num_turns, duration, per-model token split. The schema is sensible; the writer is best-effort but the exception handling is too broad (above).
- **No structured logging in the agent path.** `orchestrator.py` doesn't emit any logger calls inside `_run_query_async`. If a tool call returns garbage you discover it via the answer being wrong, not via a log. For a real platform you'd want at least one `logger.info` per tool dispatch with timing.
- **Publish-workflow guards are load-bearing.** `scripts/git-hooks/pre-commit` chains the publish guard (personal-pattern scan via `.publish-guard.local`) and `scripts/check-secrets.sh`. The hook is *not* in version control (`CLAUDE.md`: "not cloned"); `install-guards.sh` arms it. `check-secrets.sh` also runs as the first step of `smoke-test.sh`, so secret-leak protection is genuinely enforced even without the local hook. This is the right belt-and-braces.
- **Experiment scaffold (`runs/experiment/`, `src/experiment/`)** is genuinely engineered — `tick.py` is 303 lines with explicit time/spawn injection for unit testability, deterministic state machine, file-sentinel STOP/PAUSE, retry-or-block budget. `tests/unit/experiment/test_tick.py` is 691 lines. For a one-person research-loop driver this is over-engineered relative to its job (orchestrating Claude/Codex workers across phases), but the engineering is real, not pretend. The recent fix-list in `MEMORY.md` (worker→verifier result.json rename, mkdir-lock for parallel `claude -p`) shows the bugs being found are real boundary conditions, which suggests the scaffold is being exercised rather than admired.
- **`permission_mode="bypassPermissions"`** is set in both `orchestrator.py:180` and `eval/judge.py:141`. Fine for a local OAuth-backed tool, but if this code were ever lifted into a multi-tenant context (or run as a service the user didn't sit at) that line becomes a security event. Worth a comment block, not just a magic string.

---

## What I'd change first

1. **Kill the `_current_config` global in `orchestrator.py`.** Replace with `contextvars.ContextVar[Config]` or a closure factory that builds the `@tool` coroutines per-call. This unblocks any future concurrent caller (Streamlit, batch eval, FastAPI wrapper) and removes a class of subtle bugs that won't show up until they do. Roughly 30 lines of churn.
2. **Patch the Quick Start to actually run from clone.** Either (a) have `loader_async.run_ingestion_async` call `initialise_schema()` itself when the schema is missing, or (b) replace `README.md:71-81` with `./scripts/ingest.sh && ./scripts/build-index.sh`. Add an explicit precondition check that prints "Claude Code not logged in — run `claude /login`" instead of letting the SDK exception bubble. Also fix `pyproject.toml:3` to `setuptools.build_meta` while you're there.
3. **Write a real schema-migration note (`docs/MIGRATIONS.md`).** Even one paragraph per pass — "pass 28 added `AlgorithmFamily` outrigger; backfill via `scripts/backfill-algorithm-families.sh`; no destructive reset required" — would close the single gap that makes this look like a solo build log rather than a maintainable system. The retros in `runs/build-log/` have the content; it just needs to be lifted into an ordered, idempotent migration index.

Couldn't verify: actual end-to-end ingest time, judge sample variance, or whether `build-index.sh` succeeds against an empty graph (the script reads `LIMIT 100000` rows and assumes the entity tables exist).
