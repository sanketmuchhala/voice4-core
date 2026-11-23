"""Export JSON Schemas for every contract model.

    uv run python -m voice4_contracts.export          # write packages/contracts/schemas/
    uv run python -m voice4_contracts.export --check  # exit 1 if committed schemas drifted
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .audio import AudioFrame
from .compliance import ComplianceCheckResult
from .eval import CallEvalReport
from .tools import ToolCallRequest, ToolCallResult
from .turn import TurnEvent
from .version import CONTRACT_VERSION

MODELS: tuple[type[BaseModel], ...] = (
    AudioFrame,
    TurnEvent,
    ToolCallRequest,
    ToolCallResult,
    ComplianceCheckResult,
    CallEvalReport,
)

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


def render() -> dict[str, str]:
    """Filename -> exact file contents."""
    out: dict[str, str] = {}
    for model in MODELS:
        schema: dict[str, Any] = model.model_json_schema()
        schema["$comment"] = f"voice4-contracts {CONTRACT_VERSION}"
        out[f"{model.__name__}.json"] = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rendered = render()
    if args.check:
        stale = [
            name
            for name, text in rendered.items()
            if not (SCHEMA_DIR / name).exists() or (SCHEMA_DIR / name).read_text() != text
        ]
        if stale:
            print(f"schemas out of date: {', '.join(stale)}", file=sys.stderr)
            return 1
        return 0
    SCHEMA_DIR.mkdir(exist_ok=True)
    for name, text in rendered.items():
        (SCHEMA_DIR / name).write_text(text)
    print(f"wrote {len(rendered)} schemas to {SCHEMA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
