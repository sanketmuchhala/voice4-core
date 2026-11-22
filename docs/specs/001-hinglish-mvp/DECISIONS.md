# DECISIONS 001: Hinglish MVP

## D1. Streaming cascade, not native S2S, for v1. Accepted.

- **Why:** we can inspect transcripts and tool calls, swap providers, and control turn-taking fully. Benchmarks in our research showed cascades ahead of S2S on live-call reliability and accuracy, and S2S endpoints falsely interrupting on backchannels.
- **Rejected:** wrapping OpenAI Realtime or Gemini Live as the core engine. They stay available as eval comparison nodes.

## D2. No language-routing STT. Accepted.

- **Why:** mid-sentence code-switching breaks routing pipelines.

## D3. Pipecat or LiveKit Agents. Open.

- To be decided by a blind parallel prototype in Week 1, scored on the eval set (p95 latency, semantic accuracy, integration effort with our chosen carrier).

## D4. Turn detector threshold 0.85 and 1.5 s max hold. Provisional.

- These are starting values from the research brief. Confirm them on our own eval set.

## D5. Vertical for v1. Open.

- Candidates: COD confirmation, logistics verification, clinic booking.
