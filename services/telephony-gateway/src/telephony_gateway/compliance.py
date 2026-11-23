"""Pre-dial compliance guard (AGENTS.md invariant 4).

Every outbound dial MUST call `check_trai_window_and_dnd` and refuse to dial unless the
result is `allowed`. The guard fails closed: if the DND lookup errors, the dial is blocked.

Regulatory parameters (calling window, header series) come from our research brief on
TRAI TCCCPR 2018 and must be confirmed with the carrier during DLT onboarding.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, time
from typing import Protocol
from zoneinfo import ZoneInfo

from bolchaal_contracts import ComplianceCheckResult, ComplianceReason

IST = ZoneInfo("Asia/Kolkata")
CALL_WINDOW_START = time(9, 0)  # inclusive
CALL_WINDOW_END = time(21, 0)  # exclusive
# 140 = promotional, 1600/1601 = service/transactional (confirm the exact series with the carrier).
DEFAULT_HEADER_PREFIXES: tuple[str, ...] = ("140", "1600", "1601")
_HEADER_RE = re.compile(r"\d{10}")


class DndRegistry(Protocol):
    """NCPR/DND scrub backend (carrier API, cached registry, ...)."""

    def is_dnd(self, msisdn: str) -> bool: ...


@dataclass(frozen=True)
class DialRequest:
    call_id: str
    to_msisdn: str
    caller_header: str
    dlt_template_id: str | None
    consent_recorded: bool


def _header_valid(header: str, prefixes: Sequence[str]) -> bool:
    return bool(_HEADER_RE.fullmatch(header)) and header.startswith(tuple(prefixes))


def check_trai_window_and_dnd(
    req: DialRequest,
    *,
    dnd: DndRegistry,
    now: datetime | None = None,
    allowed_header_prefixes: Sequence[str] = DEFAULT_HEADER_PREFIXES,
) -> ComplianceCheckResult:
    if now is None:
        now = datetime.now(IST)
    elif now.tzinfo is None:
        raise ValueError("`now` must be timezone-aware")

    reasons: list[ComplianceReason] = []

    local = now.astimezone(IST).time()
    if not (CALL_WINDOW_START <= local < CALL_WINDOW_END):
        reasons.append(ComplianceReason.OUTSIDE_WINDOW)

    if not req.dlt_template_id or not req.dlt_template_id.strip():
        reasons.append(ComplianceReason.MISSING_DLT_TEMPLATE)

    if not _header_valid(req.caller_header, allowed_header_prefixes):
        reasons.append(ComplianceReason.INVALID_HEADER_SERIES)

    if not req.consent_recorded:
        reasons.append(ComplianceReason.NO_CONSENT)

    try:
        if dnd.is_dnd(req.to_msisdn):
            reasons.append(ComplianceReason.DND_LISTED)
    except Exception:
        reasons.append(ComplianceReason.DND_LOOKUP_FAILED)

    return ComplianceCheckResult(
        call_id=req.call_id,
        allowed=not reasons,
        reasons=tuple(reasons),
        checked_at=now,
        dlt_template_id=req.dlt_template_id,
        header=req.caller_header,
    )
