# Architecture

```text
 caller (PSTN, 8 kHz G.711u)
        |
 [1] telephony-gateway  -- Exotel WS / Twilio SIP, compliance guard, warm transfer
        |  AudioFrame (contracts)
 [2] voice-orchestrator -- VAD + acoustic turn detector, barge-in, TTS flush
        |       \
 [3] streaming STT      [4] LLM + tools  ---> tool-crm-adapter (Roman-script normalized)
   (code-switching)          |
        \____________ streaming TTS (8 kHz native)
        |
 [5] eval-harness       -- replay real 8 kHz calls, latency + semantic scoring
 [6] compliance + data  -- DLT/DND/window, DPDP consent, encryption, retention, erasure
```

## 1. Telephony transport

The framework choice is decided in Week 1 by a blind prototype shootout (see `specs/001-hinglish-mvp/DECISIONS.md`).

- **Pipecat:** FastAPI WebSocket transport with carrier serializers (Exotel, Plivo, Twilio, Telnyx, Vonage) and explicit frame-level pipeline control. It has no native SIP in core.
- **LiveKit Agents:** native SIP service in front of WebRTC rooms. It is cleaner for Tata/Airtel/Twilio SIP trunks and for browser plus phone use.

## 2. Turn detection and barge-in (starting parameters, tune with evals)

- Acoustic end-of-turn model (Smart Turn v3.x class). Decision threshold **0.85** (stock is 0.5), max hold **1.5 s**.
- VAD hysteresis: about **80 ms** onset and about **400 ms** offset.
- Interrupt debounce of **200-400 ms**. An interruption needs real words, not volume spikes, so backchannels and coughs pass through.
- On a confirmed barge-in, kill buffered TTS at the source.
- Target: **< 800 ms p95 voice-to-voice**.

## 3. Speech

- STT: one native code-switching stream. Candidates are Sarvam Saaras, Soniox Indic, and Deepgram Nova-3 for US English.
- TTS: native 8 kHz output with < 200 ms time to first audio. Candidates are Sarvam Bulbul, Smallest Lightning, Cartesia Sonic, and ElevenLabs Flash.
- Providers sit behind an interface so we can swap them with no lock-in.

## 4. LLM and tools

- Use a fast model behind a thin provider gateway (configurable).
- Mirror the caller's code-mixed register. Normalize structured entities to Roman script before tools or RAG.
- Hand off to a human when confidence is low or after 2 consecutive repair turns.

## 5. Evaluation (build in Week 1)

- Metrics: p95 turn latency, repair turns per call, semantic intent match, tool-call accuracy, false cutoff and false interrupt rates.
- Use **real recorded human 8 kHz calls**. Synthetic TTS audio badly overstates turn-detector errors and misleads tuning.

## 6. Compliance (India)

- **TRAI TCCCPR:** DLT principal-entity registration, approved headers (140 series for promotional, 1600/1601 for service/BFSI), pre-dial DND/NCPR scrub, and a 09:00-21:00 IST window. Never dial from a 10-digit mobile number.
- **DPDP Rules 2025:** consent timestamps, AES-256 at rest and TLS in transit, 1-year processing logs, and erasure covering audio and transcripts.
- **IT Rules (Feb 2026):** provenance metadata for synthetic audio.

## Scaling rules

- Inference runs in separate batching servers, never in the call worker. In-process models make TTFT jump sharply at only a few concurrent calls.
