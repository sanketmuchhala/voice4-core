# SPEC 001: Hinglish COD confirmation MVP

**Status:** Draft v0.2. Needs approval from both founders before parallel work starts.
**Contracts:** `packages/contracts` v0.1.0

## 1. Goal

An agent that places a real outbound call over 8 kHz Indian telephony and confirms a cash-on-delivery (COD) order in natural Hinglish. Success means:

- it handles interruptions with **under 800 ms p95 voice-to-voice latency**
- it writes the outcome back to the merchant's order system
- it hands off to a human when unsure
- it is TRAI/DPDP compliant end to end

**Why COD:** a D2C merchant ships a large share of orders as COD, and RTO (return-to-origin) on unconfirmed COD orders is expensive. Confirmation calls are high volume and short, with outcomes that are easy to measure.

## 2. Call flow

1. The merchant webhook reports a new COD order, and a call job is queued.
2. **Pre-dial guard:** telephony-gateway runs `check_trai_window_and_dnd()`. If it returns `allowed=False`, the job is marked `blocked`, nothing is dialed, and the verdict is logged.
3. Dial with the approved DLT header and template.
4. **Opener (fixed, DLT-registered):** "Namaste, main <brand> ki taraf se ek automated assistant bol rahi hoon, aapke order ke baare mein." This includes the AI disclosure.
5. Identity check: "Kya main <first name> se baat kar rahi hoon?" If the answer is no, the outcome is `wrong_number` and the call ends.
6. Order summary from `get_order`: item count, the headline item, the amount in rupees, and the delivery area. Then: "Kya aap yeh order confirm karte hain?"
7. Outcomes, written with `update_order_status`:
   - `confirmed` means a yes.
   - `cancelled` means a no. Ask for a reason once and record it.
   - `reschedule_requested` or `address_change_requested` goes to `transfer_to_human` if an agent is available. Otherwise record the request and promise a callback.
   - `unreachable` covers no answer, voicemail, or silence after 2 reprompts.
8. **Retries:** at most 3 attempts per order, at least 2 h apart, every attempt inside the calling window and re-checked by the guard.
9. **Handoff triggers:** 2 consecutive repair turns, the caller asking for a human, an address change, or LLM tool-arg confidence below the threshold (default 0.7).

## 3. Audio formats

| Hop | Format |
| --- | --- |
| Carrier to gateway to orchestrator | 8 kHz mono PCMU (G.711 mu-law), 20 ms frames (160 bytes), `AudioFrame(codec="pcmu", sample_rate=8000)` |
| Into VAD, Smart Turn, and any 16 kHz STT | 16 kHz mono PCM16 LE, produced by **one** explicit, tested resampler in voice-orchestrator |
| TTS output | 8 kHz PCMU natively where the provider supports it, otherwise an explicit downsample before egress |

## 4. Turn-taking state machine (voice-orchestrator)

States: `LISTENING`, `USER_SPEAKING`, `HOLD`, `THINKING`, `AGENT_SPEAKING`, `HANDOFF`, `ENDED`. Each transition that names an event emits that `TurnEvent`.

| From | Trigger | To | Emit / action |
| --- | --- | --- | --- |
| LISTENING | VAD onset (voiced for at least 80 ms) | USER_SPEAKING | `USER_SPEECH_START` |
| LISTENING | no speech 6 s after an agent question | AGENT_SPEAKING | reprompt (after 2 reprompts, outcome `unreachable`, then ENDED) |
| USER_SPEAKING | VAD offset (silent for at least 400 ms) | run Smart Turn: p >= **0.85** goes to THINKING, otherwise HOLD | `USER_TURN_END` if THINKING |
| HOLD | speech resumes | USER_SPEAKING | none |
| HOLD | Smart Turn re-evaluated with p >= 0.85 | THINKING | `USER_TURN_END` |
| HOLD | total hold reaches **1.5 s** | THINKING | `MAX_HOLD_ELAPSED`, then `USER_TURN_END` |
| THINKING | user speech starts before any TTS audio | USER_SPEAKING | cancel LLM generation (nothing to flush) |
| THINKING | first TTS audio frame | AGENT_SPEAKING | `AGENT_SPEECH_START` |
| AGENT_SPEAKING | VAD onset | (debounce window, default **300 ms**, configurable 200-400) | keep speaking |
| AGENT_SPEAKING | in the window, STT returns at least **2** non-backchannel words, **or** one stop word | USER_SPEAKING | stop TTS, drop queued frames, then `BARGE_IN` and `TTS_FLUSHED` |
| AGENT_SPEAKING | window ends with only backchannel tokens or no words | AGENT_SPEAKING | `BACKCHANNEL` (TTS is never paused) |
| AGENT_SPEAKING | TTS complete | LISTENING | `AGENT_SPEECH_END` |
| any | handoff trigger (section 2.9) | HANDOFF | `transfer_to_human` |

**Backchannel tokens** (case and script insensitive): haan, haan ji, ji, achha, accha, hmm, mm hmm, uh huh, ok, okay, theek hai, yeah, right.
**Stop words** (barge in after a single word): nahi, nahin, no, ruko, rukiye, stop, wait, ek minute, sorry.

Rules:
- A non-speech noise such as a cough produces no words, so it never causes a barge-in.
- After `TTS_FLUSHED`, no outbound audio from the interrupted utterance may reach the carrier.

## 5. Latency budget (p95, last voiced user frame to first agent audio on the wire)

| Stage | Budget |
| --- | --- |
| Endpointing (VAD offset plus Smart Turn, 32 ms on CPU) | 400-450 ms |
| STT final (overlaps with endpointing) | 0-100 ms extra |
| LLM time to first token | at most 250 ms |
| TTS time to first audio | at most 150 ms |
| Transport and jitter | at most 50 ms |

The plain sum (about 850-1000 ms) is **over budget**. To make 800 ms, voice-orchestrator must **start the LLM speculatively at VAD offset onset** and discard the result if the user resumes. See DECISIONS D6.

## 6. Service boundaries

| Boundary | Contract | Direction |
| --- | --- | --- |
| telephony-gateway to voice-orchestrator | `AudioFrame` (pcmu, 8 kHz) | both ways |
| voice-orchestrator to observers (dashboard, eval) | `TurnEvent` | out |
| voice-orchestrator to tool-crm-adapter | `ToolCallRequest` / `ToolCallResult` (hard 1.5 s timeout) | request/response |
| telephony-gateway to job queue | `ComplianceCheckResult` | out, logged |
| eval-harness to dashboard | `CallEvalReport` | out |

Transport between services is not decided yet. It will come out of the Week 1 shootout; candidates are in-process asyncio queues for v1 and a WebSocket or gRPC split later.

### Tool arguments (inside `ToolCallRequest.args`, all Roman/ASCII)

- `get_order`: `{order_id}`. Returns `{order_id, first_name, item_count, headline_item, amount_inr, pincode, status}`.
- `update_order_status`: `{order_id, status, reason?}`, where status is one of `confirmed`, `cancelled`, `reschedule_requested`, `address_change_requested`, `unreachable` or `wrong_number`.
- `transfer_to_human`: `{reason}`. Returns `{transferred: bool}`.

## 7. Compliance and data

- **TRAI:** all checks live in telephony-gateway (window, DLT template, header series, DND, consent). The guard fails closed.
- **DPDP:** store a consent timestamp per order (the merchant's checkout consent). Recordings and transcripts are encrypted at rest. Processing logs are kept for 1 year. An erasure endpoint deletes the audio, transcripts and tool payloads for a phone number.
- **Provenance:** agent audio carries provenance metadata, and `CallEvalReport.provenance_tagged` must be true.
- Phone numbers are masked (last 4 digits only) in logs and the UI.

## 8. Out of scope (v1)

Inbound calls, languages beyond Hindi, English and Hinglish, training our own models, native speech-to-speech as the primary engine (allowed as an eval comparison), a self-serve builder, multi-tenant setup, and a SOC 2 audit.
