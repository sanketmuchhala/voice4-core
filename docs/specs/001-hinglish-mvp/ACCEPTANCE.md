# ACCEPTANCE 001: Hinglish MVP

Each item is observable and tested in `apps/eval-harness` on **real recorded** 8 kHz calls unless noted.

- [ ] p95 voice-to-voice turn latency under 800 ms across the eval set
- [ ] A 400 ms cough during agent speech does not trigger a barge-in
- [ ] Backchannels ("haan", "okay", "uh huh") during agent speech do not trigger a barge-in
- [ ] A real interruption stops agent audio, and no buffered TTS tail replays afterwards
- [ ] A caller pausing for up to 1.5 s mid-sentence is not cut off
- [ ] A mixed sentence ("Mera order kab deliver hoga, order number ABC123") produces a correct tool call with `ABC123` in Roman script
- [ ] Two consecutive repair turns trigger a warm transfer to a human
- [ ] An outbound dial outside 09:00-21:00 IST, or to a DND number, is blocked and logged (unit test)
- [ ] Every call record has a consent timestamp. An erasure request removes its audio and transcripts (unit test)
- [ ] Ingress audio at 8 kHz is explicitly resampled before any 16 kHz model (unit test)
