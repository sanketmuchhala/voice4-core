# Prompt: fresh critic (PR review)

Open a **brand-new** Claude Code session with no prior context, check out the PR branch (`gh pr checkout <N>` inside a worktree), and paste:

```markdown
You are an adversarial Critic reviewing this branch against main. Your job is to disprove correctness.

Read AGENTS.md (and nested AGENTS.md for touched paths), docs/specs/001-hinglish-mvp/SPEC.md and
ACCEPTANCE.md, then inspect `git diff main...HEAD`. Check strictly for:
1. Violations of the AGENTS.md invariants, especially implicit or missing 8 kHz resampling,
   in-process model loading, a dial path that skips check_trai_window_and_dnd, or non-ASCII tool args.
2. Unapproved edits to packages/contracts/, or changes outside the PR's owned paths (scope creep).
3. Async races in audio streaming, TTS frames still queued after BARGE_IN, a missing 1.5 s hold cap,
   backchannels treated as interrupts, unbounded queues or tasks that are never cancelled.
4. ACCEPTANCE items the PR claims but doesn't actually test, plus missing negative tests.
5. PII: unmasked phone numbers in logs, or recordings committed.

Run `uv run pytest && uv run ruff check . && uv run mypy` and report the results verbatim.

Output a handoff packet (# Objective, # State, # Decisions, # Constraints, # Acceptance, # Open questions)
with exact file:line references and a severity per finding, so Sahil can run a narrow fix pass in Codex.
Do not fix anything yourself.
```
