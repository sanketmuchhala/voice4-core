from enum import StrEnum
from typing import Self

from pydantic import AwareDatetime, Field, model_validator

from ._base import ContractModel


class ComplianceReason(StrEnum):
    OUTSIDE_WINDOW = "outside_window"
    DND_LISTED = "dnd_listed"
    DND_LOOKUP_FAILED = "dnd_lookup_failed"
    MISSING_DLT_TEMPLATE = "missing_dlt_template"
    INVALID_HEADER_SERIES = "invalid_header_series"
    NO_CONSENT = "no_consent"


class ComplianceCheckResult(ContractModel):
    """Pre-dial verdict from telephony-gateway. `allowed` is True iff `reasons` is empty."""

    call_id: str = Field(min_length=1)
    allowed: bool
    reasons: tuple[ComplianceReason, ...] = ()
    checked_at: AwareDatetime
    dlt_template_id: str | None = None
    header: str | None = None

    @model_validator(mode="after")
    def _allowed_iff_no_reasons(self) -> Self:
        if self.allowed == bool(self.reasons):
            raise ValueError("allowed must be True exactly when reasons is empty")
        return self
