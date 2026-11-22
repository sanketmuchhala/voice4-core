# AGENTS.md

Shared instructions for every coding agent working in this repo (OpenAI Codex, Claude Code, Cursor, Copilot).
Keep this file short (under ~200 lines). Do not put tasks, backlogs or secrets here. Tasks go in GitHub Issues and `docs/specs/`.

## Project

Bolchaal is a low-latency Hinglish voice agent for 8 kHz telephony. Read `docs/architecture.md` before touching `services/`.

## Commands

The toolchain is not wired up yet. Update this section when it is.

- Install: `uv sync` (Python), `pnpm install` (dashboard)
- Test: `uv run pytest -q`
- Lint and typecheck: `uv run ruff check . && uv run mypy services/`
- Eval smoke test: `uv run python apps/eval-harness/run_eval.py --set smoke-8khz`

## Architecture invariants (do not violate)

1. Telephony ingress audio is 8 kHz PCM / G.711 mu-law. Resample explicitly and visibly before any 16 kHz model (VAD, turn detector, STT).
2. Never load inference models (VAD, turn detector, SLM, TTS) inside the async call-worker process. Call a separate inference server.
3. No language-routing pipeline. Use a single code-switching STT stream.
4. Every outbound dial must pass the compliance guard in `services/telephony-gateway` (DLT header, DND/NCPR scrub, 09:00-21:00 IST window).
5. Normalize IDs, phone numbers, emails, amounts and dates to Roman/ASCII before any tool call or RAG lookup.
6. On a confirmed barge-in, flush buffered TTS audio at the source. Stale tail audio must never replay.
7. Do not change `packages/contracts/` without updating the matching `SPEC.md` and contract tests in the same PR.
8. No secrets in code or docs. Use `.env` (git-ignored) and document variables in `.env.example`.

## Ownership

| Path | Owner | Agent |
| --- | --- | --- |
| `docs/specs/`, `packages/contracts/` | Sanket | Claude Code |
| `services/telephony-gateway/`, `services/tool-crm-adapter/`, `apps/ops-dashboard/` | Sanket | Claude Code |
| `services/voice-orchestrator/`, `apps/eval-harness/` | Sahil | Codex |

Stay inside your owned paths. If you need a change elsewhere, open an issue or write a handoff packet (see `docs/workflow.md`).

## Definition of done

- The relevant unit tests and the 8 kHz eval smoke test pass.
- ruff and mypy are clean, and there are no new unpinned dependencies.
- The PR links its spec in `docs/specs/` and states which `ACCEPTANCE.md` items it satisfies.
- The PR was reviewed by the other founder's agent. No agent grades its own work.

## Branches

- `main` is protected and integrates through PRs only.
- Feature branches are named `feat/<spec-id>-<slug>`, for example `feat/001-smart-turn`. Do the work in a git worktree.
