"""Eval harness entry point. Owner: Sahil (Codex).

    uv run python apps/eval-harness/run_eval.py --set smoke-8khz

Fixture sets live in apps/eval-harness/fixtures/<set>/. Real customer recordings are
NEVER committed (DPDP); keep them under recordings/ (git-ignored) and point --root at it.
Stub for now: lists what it would score and exits 0 so the DoD command works.
"""

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", dest="set_name", default="smoke-8khz")
    parser.add_argument("--root", type=Path, default=HERE / "fixtures")
    args = parser.parse_args(argv)

    set_dir: Path = args.root / args.set_name
    clips = sorted(set_dir.glob("*.wav")) if set_dir.is_dir() else []
    if not clips:
        print(f"[eval] set '{args.set_name}': no fixtures yet at {set_dir}, nothing scored")
        return 0
    print(f"[eval] set '{args.set_name}': {len(clips)} clips found, scoring not implemented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
