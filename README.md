# Bolchaal

**Bolchaal** (बोलचाल, "everyday spoken conversation") is a voice agent for high-chaos contact centers. It is built for the calls that break generic voice bots: 8 kHz phone lines, background noise, callers switching between Hindi and English mid-sentence, and people who interrupt, pause to think, or say "haan" while the agent is still talking.

The plan is to harden the stack on high-volume Indian telephony first, then take it to high-margin US verticals such as auto dealers, hospitality, healthcare and BFSI.

## What makes it different

- **Telephony-native audio.** The whole pipeline is tuned for 8 kHz G.711 mu-law narrowband audio, not 16 kHz studio microphones.
- **Code-switching first.** It uses one native Hinglish STT stream with no language-detection router, so a sentence like *"Mera EMI bounce ho gaya"* stays one sentence.
- **Turn-taking that holds up.** It uses an acoustic end-of-turn model instead of silence timers, so backchannels and coughs don't count as interruptions. Barge-in is real, and stale TTS audio is flushed immediately.
- **Measured by outcomes, not WER.** Calls are scored on semantic intent match, task completion, p95 turn latency and repair turns per call, using recordings of real human calls.
- **Compliance built in.** TRAI TCCCPR (DLT, DND scrub, calling window) and DPDP consent and retention rules are code paths, not afterthoughts.

## Status

Pre-MVP. The v1 vertical is **outbound COD order confirmation**. See [`docs/specs/001-hinglish-mvp/`](docs/specs/001-hinglish-mvp/).

Done so far: locked contracts v0.1.0, the TRAI/DPDP pre-dial guard, Roman-script normalizers, CI, and the pre-commit hook.

## Quick start

```bash
uv sync
git config core.hooksPath scripts/hooks
uv run pytest && uv run ruff check . && uv run mypy
```

Sahil: start with [`docs/handoff-to-sahil.md`](docs/handoff-to-sahil.md).

## Repo map

```text
AGENTS.md                 Shared rules for every coding agent (Codex, Claude Code, Cursor, ...)
CLAUDE.md                 Imports AGENTS.md + Claude Code-only directives
docs/
  overview.md             Problem, market, positioning
  architecture.md         The 6-layer stack
  workflow.md             How Sanket (Claude Code) and Sahil (Codex) split and review work
  handoff-to-sahil.md     Codex setup + kickoff prompt
  prompts/                Reusable prompts: adversarial test author, fresh critic
  specs/<NNN-feature>/    SPEC / PLAN / ACCEPTANCE / DECISIONS per feature
packages/contracts/       LOCKED pydantic schemas + JSON exports (AudioFrame, TurnEvent, ToolCall*, ...)
services/
  telephony-gateway/      Carrier ingress (Exotel / Twilio), compliance guard, warm transfer
  voice-orchestrator/     Streaming STT -> LLM -> TTS loop, turn detection, barge-in
  tool-crm-adapter/       CRM / webhook tools, Roman-script normalization
apps/
  eval-harness/           8 kHz call replay, latency + semantic scoring
  ops-dashboard/          Call logs, consent audit, live monitor
scripts/hooks/            Pre-commit: secret scan, ruff, mypy, contract drift
.github/                  PR template (handoff packet) + CI
```

## Parallel agent worktrees

Local worktrees live in `.worktrees/agent-N` (git-ignored via `.git/info/exclude`), one per agent session, each on its own branch. See [`docs/workflow.md`](docs/workflow.md).
