# ACCEPTANCE 001: Hinglish COD MVP

Status: (x) has a passing test, ( ) not yet. The "Covered by" column names the test that proves the item.

## Voice loop (eval-harness on **real recorded** 8 kHz calls unless noted)

| # | Criterion | Covered by |
| --- | --- | --- |
| V1 | p95 voice-to-voice turn latency under 800 ms over the eval set | ( ) eval-harness `smoke-8khz` |
| V2 | A 400 ms cough at -6 dB during agent speech causes 0 barge-ins | ( ) adversarial_voice |
| V3 | Backchannels during agent speech ("haan", "okay", "uh huh", "achha", "hmm") cause 0 barge-ins | ( ) adversarial_voice |
| V4 | The single word "nahi" or "ruko" during agent speech causes a barge-in within the debounce window | ( ) adversarial_voice |
| V5 | After a barge-in, no frame of the interrupted utterance is sent (no tail replay) | ( ) adversarial_voice |
| V6 | A mid-sentence pause under 1.5 s is not cut off; at 1.5 s the turn ends with `MAX_HOLD_ELAPSED` | ( ) adversarial_voice |
| V7 | 8 kHz PCMU ingress is resampled explicitly before any 16 kHz model (unit) | ( ) voice-orchestrator tests |
| V8 | With 3 concurrent simulated calls, no call's event loop stalls for more than 50 ms (no in-process inference) | ( ) adversarial_voice |

## Tools and normalization

| # | Criterion | Covered by |
| --- | --- | --- |
| T1 | "Mera order kab aayega, order number ABC१२३" leads to `get_order` with `order_id="ABC123"` | (x) `test_crm_normalize.py` (normalizer); ( ) end to end |
| T2 | Non-ASCII tool args are rejected at the contract | (x) `test_contracts_models.py::test_tool_args_must_be_roman` |
| T3 | Indian mobile numbers in any spoken or script form normalize to 10 digits | (x) `test_crm_normalize.py::test_phone` |
| T4 | A tool call slower than 1.5 s returns `timeout` and the agent recovers verbally | ( ) |
| T5 | Two consecutive repair turns lead to `transfer_to_human` | ( ) |

## Compliance (unit)

| # | Criterion | Covered by |
| --- | --- | --- |
| C1 | A dial at or after 21:00 IST, or before 09:00 IST, is blocked, whatever the server timezone | (x) `test_telephony_compliance.py::test_calling_window_ist`, `test_window_uses_ist_not_server_tz` |
| C2 | A dial to a DND-listed number is blocked | (x) `test_dnd_listed_blocked` |
| C3 | If the DND lookup fails, the dial is blocked (fail closed) | (x) `test_dnd_lookup_failure_fails_closed` |
| C4 | A missing DLT template is blocked | (x) `test_missing_dlt_template_blocked` |
| C5 | A caller header outside 140/1600/1601, or a plain mobile number, is blocked | (x) `test_invalid_header_blocked` |
| C6 | No recorded consent means the dial is blocked | (x) `test_no_consent_blocked` |
| C7 | The gateway cannot dial without a passing `ComplianceCheckResult` (no bypass path) | ( ) adversarial_compliance |
| C8 | An erasure request removes the audio, transcripts and tool payloads for a number | ( ) |
| C9 | Every call's agent audio is provenance-tagged | ( ) |

## Pilot exit

- At least 1 design-partner merchant running live COD confirmation calls.
- Over at least 200 live calls: outcome recorded on at least 95%, and human handoff at or below 15%.
