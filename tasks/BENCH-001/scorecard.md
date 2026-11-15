# Scorecard - BENCH-001

> Scoring rubric and anchor definitions: see `rubric.md`.
> All scores are integers 1–5. Total is the sum of all six dimensions (max 30).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-001 |
| Date scored | 2026-05-15 |
| Scorer | orchestrator |
| Brief | [brief.md](./brief.md), published with one redaction noted at its top |
| Task type | writing + research (open angle, persona-west-writing skill under test) |
| Tools scored | claude (Opus 4.7), codex (GPT-5.5 x-high), gemini (gemini-2.5-pro) |
| Cursor | void under the provenance rule in `rubric.md`: dropped from the run, underlying model not recorded |

---

## Tool provenance

Recorded from `run-log.md` and `run-bench.sh`. Where the logs hold no evidence,
the field reads "not recorded".

| Tool row | Harness | Underlying model | Provider |
|----------|---------|------------------|----------|
| claude | Claude Code (native, scripted `claude -p --model opus`) | Opus 4.7 | Anthropic |
| codex | Codex CLI (native, run manually) | GPT-5.5 x-high | OpenAI |
| cursor | Cursor (wrapper) | not recorded | not recorded |
| gemini | Gemini CLI (native, scripted) | gemini-2.5-pro | Google |

**Harness-isolation note.** Cursor was not run on this brief, so there is no
native row to diff it against. See the Cursor note below.

---

## Results

| Tool | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|------|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| claude | 5 | 5 | 4 | 5 | 5 | 5 | **29** |
| codex | 5 | 5 | 4 | 5 | 5 | 5 | **29** |
| cursor | void | void | void | void | void | void | **void** |
| gemini | 3 | 5 | 3 | 5 | 5 | 5 | **26** |

Mechanical audit (all three): 0 em dashes, 0 US spellings, 0 banned AI-tell
vocabulary, word count in band (claude 1284, codex 1930, gemini 1419), and zero
fabricated statistics or sources - every figure traces to the evidence base.
The fidelity gate (fabrication caps Correctness at 1) was not tripped by any tool.

---

## Per-tool notes

### Claude (Claude Max / Opus 4.7)

Tightest single-thesis piece: felt-versus-measured productivity as a property
of the operating model, not the tool. Strong economics doing real work (Jevons,
Brooks' "no silver bullet", Deming's control group), an honest "I do not know
yet" on the unresolved bifurcation, varied sentence length, single-sentence
landings with bite. Correctness 5: every DoD item met, concrete current-fact
hook, perfect fidelity, post only. Quality held at 4 (not 5) deliberately and
conservatively per the self-assessment rule: it spells every statistic out in
words ("nineteen per cent"), which is mannered for a stat-dense iTone piece -
the real iTone examples keep figures as numerals ("down by 8-15%", "52
programmers"). No failure observed.

### Codex (Codex Plus / GPT-5.5 x-high)

Excellent, idiomatic, strong declarative headers and closers ("It is theatre
when it avoids one"; "The thousand flowers have wilted. Good. Now we can see
the weeds"). Keeps figures as numerals, which matches the iTone examples better
than Claude's spelled-out tic. Marginally broader than Claude - covers
governance, productivity, people, regulation and scale - so slightly more
survey-like and less of a single spear, which is why Quality is 4 not 5.
Correctness 5: all DoD met, perfect fidelity, post only. No failure observed.
Fastest-to-acceptable was Claude, but Codex's 2m29s is still top-anchor.

### Cursor (Cursor Pro)

Void, not scored. The run log records Cursor as dropped because it exposed only
coding models and no model could be established, so under the provenance void
rule the row counts for and against no tool and is not a winner candidate.
Harness delta: none available, as there is no recorded model to select a native
row to diff against. The claude/codex joint-29 result stands.

### Gemini (Gemini Plus / gemini-2.5-pro)

Good Ford / River Rouge historical hook and a coherent "8% economy" thesis,
clean fidelity. Quality 3: mixes two opening hooks (gold rush *and* railroads,
against the "pick one, don't mix" rule), drifts into generic confident-blog
register in places ("The numbers are stark", "It has been a catastrophic
failure"), and uses bold/italic emphasis the style spec discourages.
Correctness 3, not 5: the artefact shipped with a three-line preamble ("It
appears the write_file tool is unavailable… I am providing the full content
below"), violating "deliver only the post". This needs a trivial manual fix
(delete three lines), which is exactly the anchor-3 case. Failure mode 5: the
tool hit a genuine failure (the harness exposed no write_file tool), surfaced
it loudly and early with an accurate diagnosis, and adapted by delivering
inline rather than failing silently - textbook good failure handling, scored
on its merits and not double-penalised for the Correctness cost already taken.
Gemini's first scripted run failed on directory-trust; that was a harness
environment misconfiguration on the orchestrator's side, not a Gemini fault,
so it does not count against Iterations, Autonomy or Time.

---

## Skill diagnostic (dual purpose)

**Common miss across all three tools:** none deployed the two signature voice
moves the `persona-west-writing` few-shot material flags - the dry parenthetical
aside ("(There used to be such a thing as a pound note BTW)") and the single
register-collision joke ("hallucinates like a micro-dosed tech bro"). All three
produced competent, analytically-correct, rule-compliant prose that reads a
shade more "house analyst" than "iTone". The skill currently carries these as
*examples* but not as items in the audit checklist, so models treat them as
optional flavour and drop them under the weight of a stat-dense brief.

**Skill action (feeds persona-west-writing, not the model ranking):** promote
"at least one dry parenthetical aside" and "exactly one register-collision
joke" from example material to soft audit-checklist items in
`writing-style.md`. Also add an explicit "prefer numerals to spelled-out
figures in stat-dense pieces" line - Claude's spelled-out-numbers tic suggests
the skill is silent on this and a model will guess wrong.

---

## Verdict

**Winner:** codex (joint-highest score, 29)

**Runner-up:** claude (joint-highest score, 29)

Claude and Codex tie on points at 29. Codex is named winner deliberately under
the no-self-favouring rule: the two are genuinely neck-and-neck, and on the one
discriminating voice detail for this specific stat-heavy brief - numerals
versus spelled-out figures - Codex is the more on-idiom against the real iTone
examples, while Claude's is the tighter single argument. A reviewer should read
this as a dead heat on quality with the tie broken away from the scorer's own
tool on principle. Gemini is a clear third on a real Correctness deviation and
a looser register, not on factual accuracy.

**Key finding (one sentence):**
On a self-contained writing brief with the persona skill pasted in for fairness,
all three frontier tools cleared every hard rule and committed zero fabrications;
they separated only on voice discipline and on whether the artefact shipped clean,
and the sharpest signal is a skill gap (missing signature voice moves) common to
all three rather than a model weakness.

**iTone post angle (optional):**
"I benchmarked four AI tools writing my newsletter. They all passed the rules
and all missed the voice in the same place - which tells you more about the
brief than the models."
