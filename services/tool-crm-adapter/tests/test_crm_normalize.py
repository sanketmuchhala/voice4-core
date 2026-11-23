from decimal import Decimal

import pytest

from bolchaal_contracts import ToolCallRequest
from tool_crm_adapter.normalize import normalize_amount, normalize_order_id, normalize_phone_in


@pytest.mark.parametrize(
    ("raw", "want"),
    [
        ("ABC123", "ABC123"),
        ("abc-123", "ABC123"),
        ("ABC १२३", "ABC123"),
        ("ord #9981-22", "ORD998122"),
        ("a b c 1 2 3", "ABC123"),
    ],
)
def test_order_id(raw: str, want: str) -> None:
    assert normalize_order_id(raw) == want


@pytest.mark.parametrize("raw", ["एबीसी123", "", "AB", "ABC😀123"])
def test_order_id_rejects_non_roman(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_order_id(raw)


@pytest.mark.parametrize(
    "raw", ["9812345678", "+91 98123-45678", "919812345678", "09812345678", "९८१२३४५६७८"]
)
def test_phone(raw: str) -> None:
    assert normalize_phone_in(raw) == "9812345678"


@pytest.mark.parametrize("raw", ["12345", "5812345678", "+1 415 555 0100"])
def test_phone_rejects(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_phone_in(raw)


@pytest.mark.parametrize(
    ("raw", "want"),
    [("₹1,299", "1299"), ("Rs. १२९९.५०", "1299.50"), ("1299 rupaye", "1299")],
)
def test_amount(raw: str, want: str) -> None:
    assert normalize_amount(raw) == Decimal(want)


def test_normalized_output_passes_contract() -> None:
    # ACCEPTANCE: "Mera order kab deliver hoga, order number ABC१२३" -> Roman tool arg
    ToolCallRequest(
        call_id="c", request_id="r", name="get_order",
        args={"order_id": normalize_order_id("ABC१२३")},
    )
