# eval-harness

**Owner:** Sahil (Codex)

This app replays 8 kHz call audio through the orchestrator and writes one `CallEvalReport` per call. It tracks p95 turn latency, repair turns, false interrupts and cutoffs, semantic intent match and tool-call accuracy.

```bash
uv run python apps/eval-harness/run_eval.py --set smoke-8khz
```

- `fixtures/<set>/` holds small synthetic or consented clips that are safe to commit.
- Real customer recordings are **never committed**. Keep them in `recordings/` (git-ignored) and pass `--root recordings`.
- Tune turn-taking on real human audio, not on TTS output.
