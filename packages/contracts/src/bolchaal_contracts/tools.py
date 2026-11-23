from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from ._base import ContractModel

ToolName = Literal["get_order", "update_order_status", "transfer_to_human"]
ArgValue = str | int | float | bool | None


class ToolCallRequest(ContractModel):
    """LLM -> tool-crm-adapter. String args must already be Roman/ASCII-normalized
    (AGENTS.md invariant 5); Devanagari digits or script in an ID is rejected here."""

    call_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    name: ToolName
    args: dict[str, ArgValue] = Field(default_factory=dict)

    @field_validator("args")
    @classmethod
    def _ascii_only(cls, v: dict[str, ArgValue]) -> dict[str, ArgValue]:
        for key, val in v.items():
            if isinstance(val, str) and not val.isascii():
                raise ValueError(f"arg {key!r} must be Roman/ASCII-normalized, got {val!r}")
        return v


class ToolCallResult(ContractModel):
    call_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    status: Literal["ok", "error", "timeout"]
    latency_ms: float = Field(ge=0)
    data: dict[str, ArgValue] = Field(default_factory=dict)
    error: str | None = None

    @model_validator(mode="after")
    def _error_iff_failed(self) -> Self:
        if self.status == "ok" and self.error is not None:
            raise ValueError("status 'ok' must not carry an error")
        if self.status != "ok" and not self.error:
            raise ValueError(f"status {self.status!r} requires an error message")
        return self
