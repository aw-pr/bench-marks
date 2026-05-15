# Task Brief — {{TASK-ID}}

> This file is the single input given to all four tools. It must be self-contained.
> All required context (type signatures, schema definitions, constraints) must be pasted
> in here — do not link to external files that other tools cannot access.

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | {{TASK-ID}} |
| Date | {{YYYY-MM-DD}} |
| Source repo | {{repo-name or "standalone"}} |
| Source issue / PR | {{link or "n/a"}} |
| Tools to run | claude, codex, cursor, gemini *(delete any not applicable)* |

---

## Spec

*Describe the task precisely. Include:*
- *What the output must be (function, file, CLI tool, document, etc.)*
- *Language, framework, or format requirements*
- *Any context from the source repo that is necessary to understand the task (paste it here)*

{{SPEC}}

---

## Constraints

*List hard constraints — things the output must NOT do or must always do.*

- {{CONSTRAINT-1}}
- {{CONSTRAINT-2}}

---

## Definition of done

*How will you know the output is acceptable? Be specific — this feeds the Correctness dimension of the rubric.*

- [ ] {{ACCEPTANCE-CRITERION-1}}
- [ ] {{ACCEPTANCE-CRITERION-2}}

---

## Context paste

*If the task requires code or schema from the source repo, paste it here verbatim.*

```
{{PASTE-CONTEXT-HERE}}
```

---

## Notes for the scorer

*Optional. Any scoring nuances to keep in mind — e.g. "boundary conditions were underspecified on purpose to test how the tool handles ambiguity".*

{{SCORER-NOTES}}
