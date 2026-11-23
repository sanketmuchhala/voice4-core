# Prompt: adversarial test author

Run this in a **separate worktree** (`git worktree add -b test/001-adversarial .worktrees/adversarial main`) in a fresh Claude Code session while Sahil builds the orchestrator.

```markdown
Act as an Adversarial Test Author. Read ONLY:
- docs/specs/001-hinglish-mvp/SPEC.md
- docs/specs/001-hinglish-mvp/ACCEPTANCE.md
- packages/contracts/
Do NOT open anything under services/voice-orchestrator/.

Write a pytest suite in tests/adversarial_voice/ and tests/adversarial_compliance/ that targets plausible bugs.
Each test cites the ACCEPTANCE id it covers:
1. V7: 8 kHz PCMU AudioFrames fed to turn detection are resampled, not mis-timed (a 20 ms frame stays 20 ms).
2. V2/V3: a 400 ms cough at -6 dB and the backchannels "uh huh", "haan", "okay", "achha" during agent speech cause no BARGE_IN.
3. V4/V5: "nahi" or a 2+ word interruption causes BARGE_IN, then TTS_FLUSHED, and no outbound frame of the old utterance is sent afterwards.
4. V6: a 1.2 s mid-sentence pause is not cut off; at 1.5 s a MAX_HOLD_ELAPSED event fires.
5. T1: Hinglish utterances with Devanagari digits produce ASCII order ids at the tool boundary.
6. V8: 3 concurrent simulated calls; fail if any event loop stalls for more than 50 ms.
7. C1-C7: dials after 21:00 IST, to DND numbers, without a DLT template, or with a mobile-number header hard-fail
   before reaching the carrier adapter, and no code path dials without a passing ComplianceCheckResult.

Generate synthetic 8 kHz PCMU fixtures in code (no real recordings). Drive the orchestrator only through
the public interface described in the SPEC; if none exists yet, define a minimal Protocol in the test package
and mark the dependent tests `xfail(strict=True, reason="awaiting orchestrator")` so they fail loudly once wired.
```
