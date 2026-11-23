from datetime import UTC, datetime

import pytest
from pydantic import BaseModel, ValidationError

from voice4_contracts import (
    AudioFrame,
    CallEvalReport,
    ComplianceCheckResult,
    ComplianceReason,
    ToolCallRequest,
    ToolCallResult,
    TurnEvent,
    TurnEventType,
)
from voice4_contracts.export import render

NOW = datetime(2026, 11, 22, 10, 0, tzinfo=UTC)

SAMPLES: list[BaseModel] = [
    AudioFrame(
        call_id="c1",
        seq=0,
        direction="inbound",
        sample_rate=8000,
        codec="pcmu",
        payload=b"\xff\x7f\x00",
        timestamp_ms=20,
    ),
    TurnEvent(call_id="c1", turn_id=3, type=TurnEventType.BARGE_IN, confidence=0.9, timestamp_ms=1),
    ToolCallRequest(call_id="c1", request_id="r1", name="get_order", args={"order_id": "ABC123"}),
    ToolCallResult(call_id="c1", request_id="r1", status="ok", latency_ms=42.0, data={"x": 1}),
    ComplianceCheckResult(call_id="c1", allowed=True, checked_at=NOW, header="1400000000"),
    CallEvalReport(
        call_id="c1",
        turns=8,
        p50_turn_latency_ms=520,
        p95_turn_latency_ms=760,
        repair_turns=1,
        false_interrupts=0,
        false_cutoffs=0,
        semantic_intent_match=0.9,
        provenance_tagged=True,
    ),
]


@pytest.mark.parametrize("model", SAMPLES, ids=lambda m: type(m).__name__)
def test_json_round_trip(model: BaseModel) -> None:
    assert type(model).model_validate_json(model.model_dump_json()) == model


@pytest.mark.parametrize("model", SAMPLES, ids=lambda m: type(m).__name__)
def test_extra_fields_rejected(model: BaseModel) -> None:
    data = model.model_dump(mode="json")
    data["unexpected"] = 1
    with pytest.raises(ValidationError):
        type(model).model_validate(data)


def test_frames_are_immutable() -> None:
    with pytest.raises(ValidationError):
        SAMPLES[0].seq = 5  # type: ignore[attr-defined]


def test_audio_payload_is_urlsafe_base64_in_json() -> None:
    assert '"payload":"_38A"' in SAMPLES[0].model_dump_json()


@pytest.mark.parametrize("rate", [16000, 44100])
def test_pcmu_must_be_8khz(rate: int) -> None:
    with pytest.raises(ValidationError):
        AudioFrame(
            call_id="c", seq=0, direction="inbound", sample_rate=rate,
            codec="pcmu", payload=b"", timestamp_ms=0,
        )


def test_pcm16_at_16khz_ok() -> None:
    AudioFrame(
        call_id="c", seq=0, direction="inbound", sample_rate=16000,
        codec="pcm16", payload=b"\x00\x00", timestamp_ms=0,
    )


@pytest.mark.parametrize("bad", ["ABC१२३", "ऑर्डर"])
def test_tool_args_must_be_roman(bad: str) -> None:
    with pytest.raises(ValidationError, match="Roman/ASCII"):
        ToolCallRequest(call_id="c", request_id="r", name="get_order", args={"order_id": bad})


def test_unknown_tool_rejected() -> None:
    with pytest.raises(ValidationError):
        ToolCallRequest(call_id="c", request_id="r", name="drop_table")


def test_tool_result_error_consistency() -> None:
    with pytest.raises(ValidationError):
        ToolCallResult(call_id="c", request_id="r", status="error", latency_ms=1)
    with pytest.raises(ValidationError):
        ToolCallResult(call_id="c", request_id="r", status="ok", latency_ms=1, error="x")


def test_compliance_allowed_iff_no_reasons() -> None:
    with pytest.raises(ValidationError):
        ComplianceCheckResult(
            call_id="c", allowed=True, reasons=(ComplianceReason.DND_LISTED,), checked_at=NOW
        )
    with pytest.raises(ValidationError):
        ComplianceCheckResult(call_id="c", allowed=False, checked_at=NOW)


def test_compliance_requires_aware_datetime() -> None:
    with pytest.raises(ValidationError):
        ComplianceCheckResult(call_id="c", allowed=True, checked_at=datetime(2026, 1, 1))


def test_eval_p95_not_below_p50() -> None:
    with pytest.raises(ValidationError):
        CallEvalReport(
            call_id="c", turns=1, p50_turn_latency_ms=500, p95_turn_latency_ms=400,
            repair_turns=0, false_interrupts=0, false_cutoffs=0,
            semantic_intent_match=1.0, provenance_tagged=True,
        )


def test_committed_schemas_not_stale() -> None:
    from voice4_contracts.export import SCHEMA_DIR

    for name, text in render().items():
        path = SCHEMA_DIR / name
        assert path.exists(), f"{name} missing: run `uv run python -m voice4_contracts.export`"
        assert path.read_text() == text, f"{name} stale: re-run the export"
