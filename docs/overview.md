# Overview

> Figures below come from our Nov 2026 research brief. Re-verify them against primary sources before using them in a pitch.

## Problem

Contact-center voice AI demos well and fails in production on real phone lines:

- **Narrowband audio.** Indian PSTN/SIP carriers (Exotel, Tata, Airtel) deliver 8 kHz G.711 audio. Models trained on 16 kHz audio reportedly lose about 35% WER on it.
- **Code-switching.** Callers mix Hindi and English mid-sentence. Language-routing pipelines stall or mangle entities.
- **Turn-taking.** Silence timers cut off callers who pause to think. Backchannels ("haan", "okay", "uh huh") and coughs trigger false barge-ins.
- **Wrong metric.** WER on synthetic audio says little about whether the call got done.

## Market signal

- India enterprise voice deployments show real ROI. Meesho's bot reportedly handles about 60k calls/day at roughly 75% lower support cost, and Bajaj Finance reports about 71% of DIY service volume handled by bots.
- Funded peers include Smallest.ai (own S2S stack), Ringg AI, Bolna AI (modular STT/LLM/TTS orchestration), Giga and Dextr AI (hotel reservations). The winners own either a **deep technical moat** (telephony, Hinglish, turn-taking, latency) or a **deep vertical wedge** (voice wired into real transactions with human handoff and compliance).

## Positioning

Bolchaal aims for both moats:

1. **Technical:** reliable sub-800 ms p95 voice-to-voice latency on noisy 8 kHz Hinglish calls, with correct turn-taking.
2. **Vertical:** one narrow transactional workflow done end to end (candidates: D2C COD confirmation, logistics verification, clinic appointment booking), with a confidence-based warm transfer to a human.

Go to market: prove the stack on high-volume Indian calls, then take it to US verticals with SOC 2, HIPAA and PCI.

## Why not wrap a speech-to-speech API?

Native S2S APIs (OpenAI Realtime, Gemini Live) are great for demos. Late-2026 benchmarks in our brief show cascaded pipelines beating them on live-call reliability and data accuracy. The same benchmarks show conversational backchannels triggering false interruptions on raw S2S endpoints. We start with a streaming cascade we can inspect and tune. S2S providers can plug in later as a comparison node in the eval harness.
