# Run Log — BENCH-001

Run metadata captured at execution time. Feeds the Iterations and Time
dimensions at scoring. Not scored here.

| Tool | Wall-clock | Prompt cycles | Notes |
|------|-----------|---------------|-------|
| codex | 2m 29s | 1 (assumed; no follow-ups reported) | Model: GPT-5.5 x-high. Fed brief.md as sole prompt. Output landed in outputs/ then relocated to codex/post.md. ~1930 words. |
| claude | 74s | 1 | Model: Opus 4.7 (`--model opus`), scripted, brief.md via stdin, isolated temp cwd. 1284 words. Clean single pass. |
| gemini | 103s | 1 | Model: gemini-2.5-pro, scripted. First attempt failed on dir-trust (harness env, ~3s, not a tool fault); re-run with GEMINI_CLI_TRUST_WORKSPACE=true succeeded. 1419 words. Tried unavailable write_file tool, surfaced it clearly, delivered post inline. |
| cursor | n/a | n/a | Dropped: Cursor exposes only frontier coding models, not meaningful for a writing brief. |
