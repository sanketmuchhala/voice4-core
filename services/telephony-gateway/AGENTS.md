# telephony-gateway

- Owner: Sanket. Other agents should open a handoff instead of editing here.
- Never dial without `check_trai_window_and_dnd(...).allowed`. Do not add a bypass flag, not even for tests. Tests inject a fake `DndRegistry` and a fixed `now`.
- Ingress frames are passed through as 8 kHz `pcmu`. Resampling belongs to voice-orchestrator, not here.
- Log every compliance verdict with its `call_id`, because DPDP requires an audit trail.
