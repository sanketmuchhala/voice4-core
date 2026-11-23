# DECISIONS 001: Hinglish COD MVP

## D1. Asynchronous modular streaming cascade, not raw speech-to-speech, for v1. Accepted.

- **Why:**
  - We can inspect every transcript and tool call.
  - We can swap STT, LLM and TTS providers per language and cost.
  - We control turn-taking and backchannel handling ourselves.
  - The benchmarks in our Nov 2026 research brief showed cascades ahead of native S2S APIs on live-call reliability and data accuracy, and S2S VAD falsely interrupting on conversational backchannels.
- **Rejected:** wrapping OpenAI Realtime or Gemini Live as the sole engine. They stay as pluggable comparison nodes in eval-harness.
- **Revisit:** when an S2S provider passes ACCEPTANCE V1-V6 on our eval set.

## D2. No language-routing STT. Accepted.

Mid-sentence Hinglish breaks detect-then-route pipelines. We use one code-switching stream.

## D3. Pipecat (Exotel WebSocket) or LiveKit Agents (SIP). Open, closes at the end of Week 1.

This is decided by a blind parallel prototype against this SPEC (see PLAN). Scoring, in order:
1. p95 latency on the eval set
2. ACCEPTANCE V2-V5
3. Effort to integrate with the carrier we can actually get DLT-onboarded with first
4. Code clarity

## D4. Smart Turn threshold 0.85 and 1.5 s max hold. Provisional.

- **Why 0.85 and not the stock 0.5:** a false cutoff (talking over a caller who is thinking) costs far more than a slightly later response. The research brief reports that 0.85 reduced premature cutoffs on live calls. The 1.5 s hold cap keeps a high threshold from turning into dead air.
- **Must confirm:** sweep 0.6-0.95 on *our* real 8 kHz Hinglish calls in eval-harness. Never tune on TTS-generated audio.

## D5. The v1 vertical is outbound COD order confirmation. Accepted (2026-11-22).

- **Why:** high volume, short scripted calls, a binary outcome that is easy to measure (RTO reduction), and it exercises the full outbound TRAI path.
- **Rejected for v1:** clinic booking (health data sensitivity, more open-ended dialogue).

## D6. Speculative LLM start to meet the 800 ms budget. Proposed.

The sequential budget in SPEC section 5 overshoots 800 ms because of the 400 ms VAD offset. Proposal: start LLM generation when VAD offset begins and discard it if the user resumes or Smart Turn says HOLD. Sahil to validate during Weeks 2-3.

## D7. Which header series for COD calls. Open.

COD confirmation is arguably a service/transactional call, not promotional. Confirm the correct series and template category with the carrier during DLT onboarding. The guard takes `allowed_header_prefixes` as configuration, so this needs no code change.
