# Workflow: Sanket (Claude Code) + Sahil (Codex)

## Principles

- **No agent grades its own work.** Every PR is reviewed by the other founder's agent.
- **Parallelize independent components and serialize shared state.** Never split a boundary that hasn't been written down in `packages/contracts/` and a `SPEC.md` first.
- **Specs over chat.** Each feature lives in `docs/specs/<NNN-slug>/` with four files:
  - `SPEC.md`: approved behavior, contracts, audio and latency requirements
  - `PLAN.md`: ordered steps and the files touched
  - `ACCEPTANCE.md`: observable pass/fail checks
  - `DECISIONS.md`: what was chosen, what was rejected, and why

## Roles

| | Sanket + Claude Code | Sahil + Codex |
| --- | --- | --- |
| Main role | Architect, integrations, critic | Builder, audio pipeline, test-driven repair |
| Owns | specs, contracts, telephony-gateway, tool-crm-adapter, ops-dashboard | voice-orchestrator, eval-harness |

## Loops

### 1. Default: Architect -> Builder -> Critic

1. Sanket drafts `SPEC.md`, `ACCEPTANCE.md` and the contracts in Claude Code plan mode. Both founders approve and merge the spec PR.
2. The builder implements it in a worktree on `feat/<id>-<slug>` until tests pass.
3. A fresh agent session from the *other* founder reviews the diff strictly against the spec.
4. Accepted findings go back as a **handoff packet** (below).

### 2. Implementer + adversarial test author (high-risk logic)

For barge-in, turn-taking and the compliance guard, one agent implements while the other writes tests that try to break it. The test author sees only `SPEC.md` and `ACCEPTANCE.md`, never the implementation.

### 3. Blind parallel prototype (ambiguous choices)

Both agents build against the same spec in separate worktrees. Both versions are scored in `apps/eval-harness` on real calls, and the winner is merged. This is used in Week 1 to choose Pipecat or LiveKit.

## Handoff packet

```markdown
# Objective
# State        (branch, commit hash, files touched)
# Decisions
# Constraints
# Acceptance   (which ACCEPTANCE.md items remain)
# Open questions
```

## Worktrees

```bash
# from the main checkout
git worktree add -b feat/001-smart-turn .worktrees/feat-001-smart-turn main
git worktree list
git worktree remove .worktrees/feat-001-smart-turn
```

`.worktrees/agent-1` through `agent-4` are general-purpose slots. Run one agent session per worktree.

## Checking that instructions loaded

- Claude Code: `/context` or `/memory`.
- Codex: `codex debug prompt-input`. Restart Codex after editing `AGENTS.md`.
