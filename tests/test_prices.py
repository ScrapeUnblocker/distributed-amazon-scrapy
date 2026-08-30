from amazon_spiders.prices import parse_amount, parse_currency, parse_price


def test_us_format():
    assert parse_price("$1,299.00") == (1299.00, "USD")


def test_eu_format():
    assert parse_price("1.234,56 EUR") == (1234.56, "EUR")


def test_gbp_symbol():
    assert parse_price("£29.99") == (29.99, "GBP")


def test_plain_integer():
    assert parse_amount("5") == 5.0


def test_none_and_empty():
    assert parse_price(None) == (None, None)
    assert parse_price("") == (None, None)
    assert parse_amount("no digits here") is None


def test_currency_code_beats_symbol():
    # An explicit ISO code wins over a symbol collision.
    assert parse_currency("kr 199 SEK") == "SEK"
