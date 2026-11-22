# SPEC 001: Hinglish MVP

**Status:** Draft. Needs approval from both founders.

## Goal

One narrow production loop: answer or place a real 8 kHz Indian phone call in Hinglish, handle interruptions naturally under 800 ms p95, run a real backend action, log semantic success, and stay TRAI/DPDP compliant.

## Vertical

TBD (pick one in Week 1). Candidates:
- D2C cash-on-delivery order confirmation
- Logistics address verification
- Clinic appointment booking

## In scope (v1)

- 1 telephony connector (Exotel WebSocket **or** Twilio SIP, decided by the Week 1 shootout)
- Streaming cascade: code-switching STT -> LLM with tools -> 8 kHz TTS
- Acoustic turn detection, interrupt debounce, and TTS flush on barge-in
- 3 webhook tools for the chosen vertical, plus warm transfer to a human
- Compliance guard: DLT header, DND scrub, 09:00-21:00 IST window, consent logging
- Eval harness running on real recorded 8 kHz calls
- A minimal ops dashboard: call list, recording, transcript, metrics, consent log

## Out of scope (v1)

- Training our own speech model or SLM
- A self-serve no-code builder or multi-tenant UI
- More than Hindi, English and Hinglish
- A SOC 2 audit (design RBAC and audit logs now, audit later)
- Native S2S as the primary engine (allowed as an eval comparison only)

## Contracts (to lock in `packages/contracts/`)

- `AudioFrame`: call_id, seq, sample_rate, codec, pcm bytes, timestamp
- `TurnEvent`: call_id, type (user_start, user_end, agent_start, agent_end, barge_in, backchannel), confidence, timestamp
- `ToolCall` / `ToolResult`: call_id, name, normalized args, latency, status
- `CallRecord`: call_id, direction, consent, compliance checks, metrics, handoff reason

## Non-functional

- p95 voice-to-voice latency under 800 ms on the eval set
- No inference inside the call worker
- All audio and transcripts encrypted at rest, with erasure supported
