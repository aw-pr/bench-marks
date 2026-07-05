# iTone draft — the benchmark that couldn't tell two frontier models apart

> Draft from BENCH-007. Voice pass still needed (run through
> persona-west-writing before publishing). British English, no em dashes,
> no AI-tell vocabulary. Length target ~1000 words.

## Angle

I ran the same coding task past Claude Opus and the frontier tier above
it, blind to each other, and scored both against a fixed rubric. They
tied at a perfect score. The post is not "which model won". It is what a
tie actually tells you, and why a saturated benchmark is measuring the
wrong thing.

## The setup

The task was a classic with a trap in it: implement an LFU (least
frequently used) cache with O(1) get and put. The naive solutions —
a heap, or re-sorting a list by frequency — look right and are actually
O(log n) or O(n). The brief called that trap out explicitly and asked for
a written structural argument for why the design is genuinely O(1), not a
timing benchmark that "proves" it empirically.

Two rows, same brief, isolated runs, no sight of each other's work.
Six rubric dimensions, scored 1 to 5: correctness, iterations to working,
code quality, failure mode, autonomy, time.

## The result

Both scored 30 out of 30. Neither took the bait. Both produced the
canonical design — a frequency-bucketed structure with a running
minimum-frequency pointer, so eviction is a direct read and never a
search. Both got there in one pass with no follow-up prompting. Both
wrote the structural proof the brief asked for instead of hand-waving.

The only difference was a fingerprint, and it never touched the score:
Opus hand-rolled its own doubly-linked list with explicit previous and
next pointers; the frontier tier delegated that to Python's built-in
`OrderedDict`, which is a linked list underneath. One is more
from-first-principles. One is fewer lines leaning on a battle-tested
standard-library structure. A reviewer would note the taste difference
and approve both.

## Why the tie is the finding

Here is the uncomfortable part for anyone who benchmarks models. When two
models both max out your rubric, your rubric has stopped measuring the
models. It is measuring the task. A well-specified kernel problem with a
known optimal solution is exactly the kind of thing frontier models have
saturated. Handing it to a bigger model and expecting a bigger number is
a category error.

There was a specific prediction going in that this task would separate
them: the bigger model should be slower — more deliberation for the same
answer. It probably was. But the rubric's time dimension had one bucket
for "under five minutes", and both landed in it, and nobody had captured
the raw wall-clock. So a real difference, if it existed, was invisible by
construction. A coarse metric launders a real gap into a tie.

## The lesson

If you are evaluating frontier models, two rules fall out of this:

1. A saturated benchmark is a solved benchmark. The moment your top
   models tie at the ceiling, the task is telling you about itself, not
   about them. Move the goalposts: ambiguous specs, larger design spaces,
   problems with no known-optimal answer, tasks where taste and
   judgement carry weight that a correctness check cannot see.

2. Coarse metrics hide the very differences you are paying to detect.
   "Under five minutes" is not a measurement, it is a bucket. If the
   thing you expect to differ is time, or cost, or token count, you have
   to capture it raw. Otherwise your instrument rounds the signal away.

The headline "two frontier models tie on a coding task" reads as a
non-result. It is the opposite. It is the clearest possible signal that
you have outgrown your test, and that the next useful benchmark is the
one your current models can still fail.

## Notes for the voice pass

- Keep the "the tie is the finding" reversal as the spine.
- The linked-list-vs-OrderedDict detail is the one concrete artefact —
  keep it, it earns the abstract point.
- Do not oversell the time hypothesis; be honest it was untestable, that
  honesty is the credibility.
- Close on the forward-looking rule (benchmark the failure edge, not the
  saturated middle) — on-brand for the AI-transformation positioning.
