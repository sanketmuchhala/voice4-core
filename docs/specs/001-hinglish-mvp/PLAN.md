# PLAN 001: Hinglish MVP (6 weeks)

| Week | Sanket (Claude Code) | Sahil (Codex) |
| --- | --- | --- |
| 1 | Lock SPEC, ACCEPTANCE and contracts. Prototype A (LiveKit + SIP). Pick the vertical. | Eval-harness skeleton. Prototype B (Pipecat + Exotel WS). Record 20-30 real 8 kHz Hinglish calls. |
| 2-3 | telephony-gateway: carrier adapter, compliance guard, consent logging. Adversarial tests for turn-taking from the spec. | voice-orchestrator: streaming STT/LLM/TTS, turn detector, debounce, TTS flush. Eval metrics. |
| 4 | tool-crm-adapter: 3 tools, Roman-script normalizer, warm transfer. Critic review of the orchestrator. | End-to-end integration. Adversarial tests for the compliance guard. Critic review of the gateway. |
| 5-6 | ops-dashboard. Onboard 2-3 paid design partners. | Latency tuning against the eval set. Production hardening. Pilot monitoring. |

Exit criteria: every item in `ACCEPTANCE.md` passes, and at least 1 design partner is running live calls.
