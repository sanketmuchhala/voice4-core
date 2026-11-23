from dataclasses import replace
from datetime import UTC, datetime

import pytest

from bolchaal_contracts import ComplianceReason as R
from telephony_gateway.compliance import IST, DialRequest, check_trai_window_and_dnd


class FakeDnd:
    def __init__(self, listed: set[str] | None = None, fail: bool = False) -> None:
        self.listed = listed or set()
        self.fail = fail

    def is_dnd(self, msisdn: str) -> bool:
        if self.fail:
            raise TimeoutError("registry down")
        return msisdn in self.listed


OK = DialRequest(
    call_id="c1",
    to_msisdn="9812345678",
    caller_header="1400012345",
    dlt_template_id="TMPL-COD-001",
    consent_recorded=True,
)
NOON = datetime(2026, 11, 23, 12, 0, tzinfo=IST)


def check(req: DialRequest = OK, now: datetime = NOON, dnd: FakeDnd | None = None) -> set[R]:
    res = check_trai_window_and_dnd(req, dnd=dnd or FakeDnd(), now=now)
    assert res.allowed == (not res.reasons)
    return set(res.reasons)


def test_happy_path_allowed() -> None:
    assert check() == set()


@pytest.mark.parametrize(
    ("h", "m", "blocked"),
    [(8, 59, True), (9, 0, False), (20, 59, False), (21, 0, True), (23, 30, True), (2, 0, True)],
)
def test_calling_window_ist(h: int, m: int, blocked: bool) -> None:
    got = check(now=NOON.replace(hour=h, minute=m))
    assert (R.OUTSIDE_WINDOW in got) is blocked


def test_window_uses_ist_not_server_tz() -> None:
    assert check(now=datetime(2026, 11, 23, 15, 29, tzinfo=UTC)) == set()  # 20:59 IST
    assert R.OUTSIDE_WINDOW in check(now=datetime(2026, 11, 23, 15, 30, tzinfo=UTC))  # 21:00 IST


def test_naive_datetime_rejected() -> None:
    with pytest.raises(ValueError):
        check_trai_window_and_dnd(OK, dnd=FakeDnd(), now=datetime(2026, 11, 23, 12))


def test_dnd_listed_blocked() -> None:
    assert check(dnd=FakeDnd({"9812345678"})) == {R.DND_LISTED}


def test_dnd_lookup_failure_fails_closed() -> None:
    assert check(dnd=FakeDnd(fail=True)) == {R.DND_LOOKUP_FAILED}


@pytest.mark.parametrize("tmpl", [None, "", "   "])
def test_missing_dlt_template_blocked(tmpl: str | None) -> None:
    assert check(replace(OK, dlt_template_id=tmpl)) == {R.MISSING_DLT_TEMPLATE}


BAD_HEADERS = [
    "+919812345678",  # plain mobile number: never allowed as caller header
    "9812345678",
    "140001234",  # too short
    "14000123456",  # too long
    "1700012345",  # wrong series
    "1600ABC123",
]


@pytest.mark.parametrize("header", BAD_HEADERS)
def test_invalid_header_blocked(header: str) -> None:
    assert check(replace(OK, caller_header=header)) == {R.INVALID_HEADER_SERIES}


@pytest.mark.parametrize("header", ["1400012345", "1600012345", "1601012345"])
def test_valid_header_series(header: str) -> None:
    assert check(replace(OK, caller_header=header)) == set()


def test_no_consent_blocked() -> None:
    assert check(replace(OK, consent_recorded=False)) == {R.NO_CONSENT}


def test_multiple_reasons_reported() -> None:
    bad = replace(OK, dlt_template_id=None, caller_header="9812345678")
    got = check(bad, now=NOON.replace(hour=22), dnd=FakeDnd({"9812345678"}))
    assert got == {R.OUTSIDE_WINDOW, R.MISSING_DLT_TEMPLATE, R.INVALID_HEADER_SERIES, R.DND_LISTED}
