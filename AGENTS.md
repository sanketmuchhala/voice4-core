# AGENTS.md

Shared instructions for every coding agent in this repo (OpenAI Codex, Claude Code, Cursor, Copilot).
Keep this file under 200 lines. No tasks, backlogs, file tours or secrets: tasks go in GitHub Issues and `docs/specs/`.
Folders may have their own `AGENTS.md`. The file closest to the code wins.

## Project

Bolchaal is a low-latency Hinglish voice agent for 8 kHz telephony. The v1 vertical is outbound COD order confirmation.
Read `docs/specs/001-hinglish-mvp/SPEC.md` before changing behavior, and `docs/architecture.md` for context.

## Setup (once per clone)

```bash
uv sync                                   # Python 3.12+ workspace: packages/* and services/*
git config core.hooksPath scripts/hooks   # pre-commit: secret scan, ruff, mypy, contract drift
cp .env.example .env                      # fill locally; never commit
```

## Commands

```bash
uv run pytest                                              # all tests
uv run ruff check .                                        # lint (add --fix to autofix)
uv run mypy                                                # strict typecheck (paths set in pyproject.toml)
uv run python -m bolchaal_contracts.export [--check]       # (re)generate or verify contract JSON schemas
uv run python apps/eval-harness/run_eval.py --set smoke-8khz   # eval smoke test
```

The dashboard (`apps/ops-dashboard`) has no JS toolchain yet. Its pnpm commands will be added here when it does.

## Architecture invariants (do not violate)

1. Telephony audio is 8 kHz PCMU (G.711 mu-law). Resample explicitly, in one tested function, before any 16 kHz model (VAD, turn detector, STT).
2. No inference models (VAD, turn detector, STT, TTS, LLM) inside the async call-worker process. Call external or batching servers.
3. No language-routing pipeline. Use one code-switching STT stream.
4. Every outbound dial must pass `telephony_gateway.check_trai_window_and_dnd()` and dial only when `allowed`. There is no bypass, and it fails closed.
5. Normalize IDs, phone numbers, emails, amounts and dates to Roman/ASCII (`tool_crm_adapter.normalize`) before any tool call or RAG lookup.
6. On a confirmed barge-in, stop TTS and drop all queued outbound frames at the source. Stale tail audio must never replay.
7. `packages/contracts/` is locked. Changing it needs a SPEC update, a version bump, re-exported schemas and approval from both founders (see `packages/contracts/AGENTS.md`).
8. No secrets in code or docs. Use `.env` (git-ignored). Document variable names in `.env.example`.
9. No real customer recordings or unmasked phone numbers in git, logs or test fixtures.

## Ownership

| Path | Owner | Agent |
| --- | --- | --- |
| `docs/specs/`, `packages/contracts/` | Sanket | Claude Code |
| `services/telephony-gateway/`, `services/tool-crm-adapter/`, `apps/ops-dashboard/` | Sanket | Claude Code |
| `services/voice-orchestrator/`, `apps/eval-harness/` | Sahil | Codex |

Stay inside your owned paths. For a change elsewhere, open an issue or hand off with a handoff packet (`.github/pull_request_template.md`).

## Definition of done

- `uv run pytest`, `uv run ruff check .`, `uv run mypy` and the eval smoke test all pass, and CI is green.
- New behavior has tests. Dependencies are added via `uv add` so `uv.lock` pins them.
- The PR uses the handoff-packet template, links its spec, and lists the ACCEPTANCE items it satisfies.
- It was reviewed by the **other** founder's agent. No agent grades its own work.

## Git

- `main` is integrated through PRs only. Branches are named `feat/<spec-id>-<slug>` (for example `feat/001-turn-state-machine`) or `proto/<slug>`.
- Work in a git worktree, one agent session per worktree (`git worktree add -b <branch> .worktrees/<name> main`).

## Style

- Python 3.12+, fully typed (`mypy --strict`), pydantic v2 for anything crossing a service boundary.
- Tests sit next to their package in `tests/`, and test file names are unique repo-wide (`test_<area>_<thing>.py`).
