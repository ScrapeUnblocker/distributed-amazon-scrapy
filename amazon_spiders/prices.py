"""Price parsing helpers.

Amazon renders prices as human strings like ``$1,299.00``, ``£29.99`` or
``1.234,56 EUR``. We keep the raw string on the item and additionally expose a
normalised ``(amount, currency)`` so downstream consumers can sort and filter.
"""

from __future__ import annotations

import re

# Common currency symbols mapped to ISO-4217 codes.
_SYMBOLS = {
    "$": "USD",
    "US$": "USD",
    "C$": "CAD",
    "A$": "AUD",
    "£": "GBP",
    "€": "EUR",
    "₹": "INR",
    "¥": "JPY",
    "R$": "BRL",
    "MX$": "MXN",
    "zł": "PLN",
    "kr": "SEK",
}

_CODE_RE = re.compile(r"\b([A-Z]{3})\b")
_NUMBER_RE = re.compile(r"\d[\d.,\s]*\d|\d")


def parse_currency(text: str | None) -> str | None:
    """Best-effort currency detection from a price string."""
    if not text:
        return None
    # A trailing/leading ISO code wins (e.g. "1.234,56 EUR").
    code = _CODE_RE.search(text)
    if code:
        return code.group(1)
    # Longest symbol match first so "US$" beats "$".
    for symbol in sorted(_SYMBOLS, key=len, reverse=True):
        if symbol in text:
            return _SYMBOLS[symbol]
    return None


def parse_amount(text: str | None) -> float | None:
    """Extract a numeric amount, tolerating US (1,299.00) and EU (1.299,00) formats."""
    if not text:
        return None
    match = _NUMBER_RE.search(text)
    if not match:
        return None
    raw = match.group(0).replace(" ", "")

    last_dot = raw.rfind(".")
    last_comma = raw.rfind(",")
    if last_dot == -1 and last_comma == -1:
        digits = raw
    elif last_comma > last_dot:
        # Comma is the decimal separator: 1.299,00 -> 1299.00
        digits = raw.replace(".", "").replace(",", ".")
    else:
        # Dot is the decimal separator: 1,299.00 -> 1299.00
        digits = raw.replace(",", "")

    try:
        return float(digits)
    except ValueError:
        return None


def parse_price(text: str | None) -> tuple[float | None, str | None]:
    """Return ``(amount, currency)`` parsed from a price string."""
    return parse_amount(text), parse_currency(text)
