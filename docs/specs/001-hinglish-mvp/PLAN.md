# PLAN 001: Hinglish COD MVP (6 weeks)

## Ownership

| Path | Owner (agent) |
| --- | --- |
| `docs/specs/`, `packages/contracts/` | Sanket (Claude Code). Contract changes need both founders. |
| `services/telephony-gateway/`, `services/tool-crm-adapter/`, `apps/ops-dashboard/` | Sanket (Claude Code) |
| `tests/adversarial_voice/`, `tests/adversarial_compliance/` | Sanket (Claude Code), written from SPEC and ACCEPTANCE only |
| `services/voice-orchestrator/`, `apps/eval-harness/` | Sahil (Codex, in isolated git worktrees) |
| Adversarial tests for gateway and CRM adapter | Sahil (Codex), written from SPEC only |

## Week 0 (done: bootstrap)

The contracts v0.1.0 are locked with tests and JSON schemas. The compliance guard and normalizers are implemented. Skeletons, the pre-commit hook, CI and the PR template are in place.

## Week 1: lock the spec and run the blind shootout

- **Day 1 (both):** review and approve this SPEC, ACCEPTANCE and contracts. Merge them.
- **Days 1-3: blind parallel prototype.** Each prototype implements just the turn-taking loop from SPEC section 4 plus an echo LLM, against one real phone line:
  - Sanket (Claude Code), worktree `proto/livekit-sip`: LiveKit Agents over SIP.
  - Sahil (Codex), worktree `proto/pipecat-exotel`: Pipecat over an Exotel AgentStream WebSocket.
  - Neither of you reads the other's branch until the scoring.
- **Day 4:** score both in eval-harness on the same 20-30 real Hinglish 8 kHz calls (p95 latency, V2-V5). Record the result in DECISIONS D3. The losing branch is archived.
- **In parallel:**
  - Sanket starts DLT principal-entity registration and carrier onboarding.
  - Sahil builds the eval-harness replay and latency metrics.

## Weeks 2-3: build the core in parallel

- **Sahil:**
  - voice-orchestrator on the winning framework, covering the full section 4 state machine, the resampler, provider adapters (STT and TTS candidates from `docs/architecture.md`), and speculative LLM start (D6)
  - `CallEvalReport` output
- **Sanket:**
  - telephony-gateway carrier adapter, wired to the compliance guard with no bypass, plus consent and verdict logging
  - adversarial tests V2-V6, V8 and C7, written blind from the spec

## Week 4: integration

- **Sanket:**
  - tool-crm-adapter: `get_order`, `update_order_status` and `transfer_to_human` against a mock merchant API, then a real one
  - the 1.5 s timeout
  - Critic review of the orchestrator PRs
- **Sahil:**
  - end-to-end wiring
  - adversarial tests for the gateway and the CRM adapter
  - Critic review of Sanket's PRs
- **Exit:** a full COD call works on a real line.

## Weeks 5-6: pilot

- **Sanket:**
  - ops-dashboard
  - erasure endpoint (C8)
  - onboard 2-3 design-partner merchants
- **Sahil:**
  - latency tuning against V1
  - the Smart Turn threshold sweep (D4)
  - production hardening and pilot monitoring
- **Exit:** the pilot exit criteria in ACCEPTANCE are met.
