from typing import Self

from pydantic import Field, model_validator

from ._base import ContractModel
from .version import CONTRACT_VERSION


class CallEvalReport(ContractModel):
    """Per-call scorecard produced by apps/eval-harness (see ACCEPTANCE 001)."""

    call_id: str = Field(min_length=1)
    turns: int = Field(ge=0)
    p50_turn_latency_ms: float = Field(ge=0)
    p95_turn_latency_ms: float = Field(ge=0)
    repair_turns: int = Field(ge=0)
    false_interrupts: int = Field(ge=0)
    false_cutoffs: int = Field(ge=0)
    semantic_intent_match: float = Field(ge=0.0, le=1.0)
    tool_call_accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    handoff_reason: str | None = None
    provenance_tagged: bool = Field(description="Synthetic agent audio carried provenance metadata")
    contract_version: str = CONTRACT_VERSION

    @model_validator(mode="after")
    def _p95_ge_p50(self) -> Self:
        if self.p95_turn_latency_ms < self.p50_turn_latency_ms:
            raise ValueError("p95 latency cannot be below p50")
        return self
