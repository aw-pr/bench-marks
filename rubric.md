# Scoring Rubric

All dimensions are scored 1–5. Use integer scores only. Half-points are not permitted — if you are between two anchors, pick the lower one and note why in the "notes / surprises" field.

---

## Dimensions

### 1. Correctness
Does the output meet the brief's definition of done?

| Score | Anchor |
|-------|--------|
| 1 | Output does not meet the brief. Key requirements missing or wrong. Would not pass a basic smoke test. |
| 3 | Mostly correct. Meets the core requirement but has edge-case failures, minor spec deviations, or requires small manual fixes to be usable. |
| 5 | Fully correct. Meets every requirement in the brief, passes all stated acceptance criteria, handles the edge cases the brief specifies. |

---

### 2. Iterations to working
How many distinct prompt/fix cycles were needed before the output was acceptable?

| Score | Anchor |
|-------|--------|
| 1 | Five or more cycles, or the tool never reached an acceptable state regardless of prompting. |
| 3 | Two to three cycles. Some clarification or correction prompts were needed. |
| 5 | One cycle (the initial prompt). Output was acceptable without follow-up prompting. |

---

### 3. Code / output quality
Readability, structure, idiom, and absence of unnecessary complexity.

| Score | Anchor |
|-------|--------|
| 1 | Hard to read or maintain. Non-idiomatic, tangled, or bloated. A reviewer would request significant rewrite. |
| 3 | Serviceable. Some rough edges or style departures, but the intent is clear and the structure is defensible. |
| 5 | Clean, idiomatic, and well-structured. A reviewer would approve with at most minor nits. |

---

### 4. Failure mode
How did the tool fail when it failed? Silent-wrong is the worst outcome; loud-and-early is the best.

| Score | Anchor |
|-------|--------|
| 1 | Failure was silent or confidently wrong: the tool produced plausible-looking output that was incorrect, and gave no signal that something was wrong. |
| 3 | Failure was partially surfaced: the tool flagged uncertainty or produced an error, but the message was vague or pointed in the wrong direction. |
| 5 | Failure was loud and early: the tool identified what it could not do, asked a clarifying question, or produced a clear error with a useful diagnosis before investing significant effort. |

> Note: if the tool did not fail on this task, score 5 by default and note "no failure observed".

---

### 5. Autonomy
How much hand-holding was required beyond the initial brief?

| Score | Anchor |
|-------|--------|
| 1 | Required repeated clarifications, decisions, or approvals from the operator to make progress. Could not proceed without prompting at multiple points. |
| 3 | Required one or two clarifying exchanges but then proceeded independently. |
| 5 | Completed the task without asking any questions or requiring operator decisions beyond the initial brief. |

---

### 6. Time to acceptable result
Elapsed wall-clock time from submitting the brief to having an acceptable output (include iteration time).

| Score | Anchor |
|-------|--------|
| 1 | More than 30 minutes, or task was abandoned. |
| 3 | 5–30 minutes. |
| 5 | Under 5 minutes. |

---

## Notes / surprises

Free-text field. Record anything the rubric dimensions do not capture: unexpected behaviours, hallucinations, tool-specific quirks, interesting failure modes, or context about why a score was set where it was.

---

## Worked example

Task: implement a deterministic Gray-Scott reaction-diffusion step function in Python (see `tasks/EXAMPLE-001/`).

| Tool | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | Total |
|------|-------------|------------|---------|--------------|----------|------|-------|
| claude | 5 | 5 | 4 | 5 | 5 | 5 | 29 |
| codex | 4 | 3 | 3 | 3 | 4 | 4 | 21 |
| cursor | 3 | 3 | 4 | 3 | 3 | 3 | 19 |
| gemini | 4 | 4 | 3 | 4 | 4 | 4 | 23 |

Notes: Claude produced a working NumPy implementation on the first pass. Codex produced correct output but used a non-standard loop structure requiring one cleanup pass. Cursor's autocomplete conflated Gray-Scott with a different PDE before self-correcting. Gemini asked one clarifying question about boundary conditions before proceeding — appropriate caution, minor autonomy deduction. This row is an EXAMPLE and not real benchmark data.
