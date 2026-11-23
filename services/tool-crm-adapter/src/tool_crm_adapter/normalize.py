"""Roman/ASCII normalization for structured entities (AGENTS.md invariant 5).

Runs on STT output before any tool call or RAG lookup. Spelled-out numbers
("teen sau", "three hundred") are out of scope here; that's the LLM's job, and its
output still passes through these functions.
"""

import re
from decimal import Decimal, InvalidOperation

_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_ORDER_SEPARATORS = re.compile(r"[\s\-_./#]+")
_ORDER_ID = re.compile(r"[A-Z0-9]{4,32}")
_INDIAN_MOBILE = re.compile(r"[6-9]\d{9}")


def to_ascii_digits(text: str) -> str:
    """Map Devanagari digits to ASCII; leave everything else untouched."""
    return text.translate(_DIGITS)


def normalize_order_id(raw: str) -> str:
    """'abc-१२३ 45' -> 'ABC12345'. Raises ValueError if anything non-ASCII remains."""
    cleaned = _ORDER_SEPARATORS.sub("", to_ascii_digits(raw)).upper()
    if not _ORDER_ID.fullmatch(cleaned):
        raise ValueError(f"not a Roman/ASCII order id: {raw!r}")
    return cleaned


def normalize_phone_in(raw: str) -> str:
    """Indian mobile to 10 digits: '+91 98123-45678' / '०९८१२३४५६७८' -> '9812345678'."""
    digits = re.sub(r"\D", "", to_ascii_digits(raw))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if not _INDIAN_MOBILE.fullmatch(digits):
        raise ValueError(f"not an Indian mobile number: {raw!r}")
    return digits


def normalize_amount(raw: str) -> Decimal:
    """'₹1,299.50' / 'Rs. १२९९' / '1299 rupaye' -> Decimal('1299.50')."""
    text = to_ascii_digits(raw).replace(",", "")
    match = re.search(r"\d+(?:\.\d{1,2})?", text)
    if not match:
        raise ValueError(f"no amount in {raw!r}")
    try:
        return Decimal(match.group())
    except InvalidOperation as exc:  # pragma: no cover - regex guarantees a valid literal
        raise ValueError(f"bad amount {raw!r}") from exc
