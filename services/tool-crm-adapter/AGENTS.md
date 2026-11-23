# tool-crm-adapter

- Owner: Sanket.
- Every string argument goes through `normalize.*` before it reaches a merchant API. The contract rejects non-ASCII arguments.
- Tool calls have a hard timeout (spec: 1.5 s). If a call times out, return `status="timeout"`. Never block the voice loop.
- Never log full phone numbers. Mask all but the last 4 digits.
