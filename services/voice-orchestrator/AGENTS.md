# voice-orchestrator

- Owner: Sahil (Codex).
- The SPEC 001 section 4 state machine is the source of truth. If behavior must differ, change the spec first.
- Resample 8 kHz PCMU to 16 kHz PCM16 in one named, tested function. Never resample implicitly inside a provider adapter.
- No model weights in this process. VAD, Smart Turn, STT, TTS and LLM are reached over the network or IPC, which keeps the event loop non-blocking.
- On `BARGE_IN`, cancel TTS synthesis **and** drop any queued outbound frames before emitting `TTS_FLUSHED`.
- Put every tunable (thresholds, debounce, hold cap) in one config object with the SPEC defaults.
