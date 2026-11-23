# Handoff to Sahil (Codex)

## 1. Setup (once)

```bash
git clone https://github.com/sanketmuchhala/bolchaal.git && cd bolchaal
uv sync
git config core.hooksPath scripts/hooks
```

1. Open the repo in Codex and **mark it as trusted**. Untrusted repos don't load `AGENTS.md`.
2. Check that the instructions loaded. Run `codex debug prompt-input`, or `codex --ask-for-approval never "Summarize the current instructions."`. You should see the 9 architecture invariants and the ownership table.
3. Restart Codex whenever `AGENTS.md` (root or nested) changes, because it reads instructions once per run.
4. Work in your own worktree:

```bash
git worktree add -b proto/pipecat-exotel .worktrees/proto-pipecat main            # Week 1 shootout
git worktree add -b feat/001-eval-harness .worktrees/feat-001-eval-harness main    # in parallel
```

## 2. Kickoff prompt (paste into Codex, inside the worktree)

```markdown
# Objective
You are the Builder for `services/voice-orchestrator/` and `apps/eval-harness/` in the Bolchaal repo.
Week 1 goals:
(a) In this worktree, build a Pipecat prototype over an Exotel AgentStream WebSocket that implements
    ONLY the turn-taking state machine in docs/specs/001-hinglish-mvp/SPEC.md section 4, with an echo LLM.
    This is a blind shootout: do not read any `proto/livekit-*` branch.
(b) In a second worktree, build apps/eval-harness: replay 8 kHz WAV clips, measure per-turn
    voice-to-voice latency, and emit one `bolchaal_contracts.CallEvalReport` per call.

# State
- Branch: the one this worktree is on. Base: `main` (bootstrap commit; `git log -1 main`).
- Done: contracts v0.1.0 (`packages/contracts`), the compliance guard, normalizers, CI, and the pre-commit hook.
- voice-orchestrator and eval-harness are empty skeletons. `apps/eval-harness/run_eval.py` is a stub.

# Decisions
- Asynchronous modular cascade, not native S2S (DECISIONS D1). One code-switching STT stream, no routing (D2).
- Smart Turn threshold 0.85, max hold 1.5 s, VAD 80 ms onset / 400 ms offset, interrupt debounce
  300 ms (200-400 configurable), at least 2 non-backchannel words or 1 stop word to barge in (SPEC section 4).
- Speculative LLM start at VAD offset is proposed to hit 800 ms p95 (D6). Measure it.

# Constraints
- Read AGENTS.md and services/voice-orchestrator/AGENTS.md first. Every invariant is binding, especially:
  explicit 8 kHz -> 16 kHz resampling in one function; no models in the call-worker process;
  drop all queued TTS frames on barge-in.
- Do NOT edit packages/contracts/, services/telephony-gateway/ or services/tool-crm-adapter/.
  If a contract is missing something, stop and write the need under "Open questions" in the PR.
- Put every tunable in a single config object with the SPEC defaults.
- `uv add` for dependencies. `uv run pytest && uv run ruff check . && uv run mypy` must pass.

# Acceptance
Target items: V1, V5, V6, V7 (with tests), and eval-harness emitting valid CallEvalReport JSON.
Sanket writes V2-V6 and V8 adversarial tests blind from the SPEC. Expect them to break things.

# Open questions
- Can Exotel AgentStream deliver 8 kHz PCMU frames directly, or do we need to transcode?
- Which STT provider gives us the lowest real Hinglish 8 kHz WER for our first adapter?

When done, open a PR using .github/pull_request_template.md. Sanket's fresh Claude Code session will review it as Critic.
```

## 3. Rules of the road

- No agent grades its own work. Your PRs are reviewed by Claude Code, and you review Sanket's with Codex.
- If you think the SPEC is wrong, open a PR against the SPEC first. Don't route around it in code.
