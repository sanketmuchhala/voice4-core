# telephony-gateway

**Owner:** Sanket (Claude Code)

This service handles carrier ingress and egress (Exotel AgentStream WebSocket or Twilio/SIP, decided by the Week 1 shootout). It contains the pre-dial compliance guard and handles warm transfer to a human.

- `compliance.check_trai_window_and_dnd()` is implemented and tested. It checks the 09:00-21:00 IST window, the DLT template, the header series, consent and DND, and fails closed.
- Carrier adapter, consent logging and warm transfer are still TODO.

It emits `AudioFrame`s (8 kHz PCMU) to voice-orchestrator and produces `ComplianceCheckResult`.
