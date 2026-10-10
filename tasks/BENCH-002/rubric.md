# Adjudicator Rubric — Research Sweep Quality

**Audience:** A senior technology or AI-transformation leader in a UK-regulated financial
services firm. The output must be actionable for board reporting, regulatory programme
planning, and senior stakeholder briefings. It is not a general overview for a lay reader.

**Task for the adjudicator:** Score each blinded summary independently on the five
dimensions below. For each dimension, assign an integer score 1–5 using the anchors
provided. Do not compare labels against each other — score each against the brief and
these anchors only.

Return a single JSON object per label. Schema is defined at the end of this rubric.

---

## Dimension 1 — Brief coverage

Does the summary address the specific sub-questions raised in the research brief?

The brief has four thematic blocks:
- EU AI Act obligations and enforcement reality (GPAI timeline, Code of Practice, AI omnibus,
  extraterritorial reach)
- UK approach and the FCA Mills Review (five principles, sectoral-regulator stance, UK AI Bill
  likelihood, FCA AI Lab)
- Financial-services regime already binding AI (PRA SS1/23, Consumer Duty, SMCR, DORA, UK GDPR,
  Treasury Committee, EBA/Basel)
- Outlook, divergence, and leadership implications (compliance cost, operating model, governance
  capabilities, 2027–2030 roadmap)

| Score | Anchor |
|-------|--------|
| 1 | Two or more thematic blocks are absent or handled at a surface level with no specific detail. |
| 3 | All four blocks are present but one or two sub-questions within a block are unanswered or handled with vague generality. |
| 5 | All four blocks addressed in depth. Named instruments, timelines, and obligations are cited where the brief asks for them. No thematic block is materially thinner than the others. |

---

## Dimension 2 — Accuracy and grounding

Are the specific claims in the summary (dates, regulatory instrument names, fine levels,
enforcement timelines) accurate and grounded in evidence rather than plausible-sounding
confabulation?

| Score | Anchor |
|-------|--------|
| 1 | Multiple factual errors or invented specifics (wrong dates, wrong fine thresholds, non-existent instruments). Confident assertions that appear fabricated. |
| 3 | Mostly accurate but contains one or two unverifiable claims presented with unwarranted confidence, or vague where the brief asked for specific figures. |
| 5 | All named instruments, dates, and figures can be traced to real documents. Where uncertainty exists, the summary signals it. No evidence of confabulation. |

---

## Dimension 3 — Synthesis depth

Does the summary synthesise across sources and lanes into coherent analytical conclusions,
or does it report findings lane-by-lane without integration?

| Score | Anchor |
|-------|--------|
| 1 | Reads as a list of facts or a topic-by-topic summary. No attempt to draw cross-cutting conclusions or identify tensions between findings. |
| 3 | Makes some cross-cutting points but synthesis is uneven — strong in one area, absent in another. Tensions between regulatory regimes identified but not analysed. |
| 5 | Explicitly draws out tensions (EU vs UK divergence, principles-based vs prescriptive, technology-neutral vs AI-specific), identifies implications, and frames a coherent analytical narrative that a senior leader could use without further synthesis work. |

---

## Dimension 4 — Usefulness for a regulated financial-services audience

Would a senior technology leader in a regulated UK financial services firm find this
immediately actionable for their planning horizon?

Consider: Does the summary identify what obligations bind the firm now and when? Does it
give concrete leadership implications (governance, model inventory, SMCR mapping, vendor
due diligence)? Does it address the 2027–2030 planning horizon the brief asked for?

| Score | Anchor |
|-------|--------|
| 1 | Generic enough to apply to any regulated industry. No firm-specific instruments. No actionable leadership guidance. Could have been produced without the brief. |
| 3 | Contains FS-specific content (e.g. PRA, FCA, Consumer Duty) but leadership implications are abstract ("firms must be prepared") rather than specific ("SS1/23 model governance requirements apply to foundation models used in pricing"). |
| 5 | Directly actionable. Identifies specific instruments binding UK FS firms, names the relevant sub-areas of each, gives concrete capabilities a technology leader must own, and frames the 2027–2030 planning obligation explicitly. |

---

## Dimension 5 — Prose quality

Does the prose meet publication standard for a senior professional audience?

Assess: clarity, concision, British English, no AI-tell vocabulary (delve, leverage, seamless,
robust, game-changer, paradigm shift, etc.), analytical rather than promotional register, short
paragraphs with specific nouns.

| Score | Anchor |
|-------|--------|
| 1 | Heavy AI-tell vocabulary, corporate-deck adjectives, or promotional register. Long rambling paragraphs. Hedging openers. |
| 3 | Serviceable prose with occasional lapses — one or two clichés, some padding, or mild stylistic unevenness. Readable but would need editing before publication. |
| 5 | Publication-ready. Dry, analytical, specific. Active voice. British English. No banned vocabulary. A sub-editor would mark it lightly or not at all. |

---

## Output schema

Return a JSON object with this exact shape. Do not add fields; do not omit fields.

```json
{
  "label": "A",
  "scores": {
    "brief_coverage": 0,
    "accuracy_grounding": 0,
    "synthesis_depth": 0,
    "fs_audience_usefulness": 0,
    "prose_quality": 0
  },
  "total": 0,
  "notes": {
    "brief_coverage": "one sentence explaining the score",
    "accuracy_grounding": "one sentence explaining the score",
    "synthesis_depth": "one sentence explaining the score",
    "fs_audience_usefulness": "one sentence explaining the score",
    "prose_quality": "one sentence explaining the score",
    "overall": "two to three sentences on the summary's strongest and weakest aspects"
  }
}
```

Scores must be integers 1–5. `total` is the sum of the five scores (max 25).
