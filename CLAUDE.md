@AGENTS.md

## Claude Code only

- Use plan mode before changing `packages/contracts/`, auth, telephony webhooks, the compliance guard, or the turn-taking state machine.
- When asked to review a PR as the Critic, use a fresh session. Try to disprove the diff strictly against the linked `SPEC.md` and `ACCEPTANCE.md`. Look for audio-buffer leaks, race conditions, missing 8 kHz tests, scope creep, and TRAI/DPDP violations.
- When writing adversarial tests for Sahil's work, read only `SPEC.md` and `ACCEPTANCE.md`, not the implementation.
