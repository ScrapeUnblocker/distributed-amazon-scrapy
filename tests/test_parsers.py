from amazon_spiders.parsers import asin_from_url, next_page_url, parse_product, parse_search

from .conftest import load_response


def test_parse_search_extracts_products():
    response = load_response("search.html", "https://www.amazon.com/s?k=wireless+headphones")
    rows = list(parse_search(response, "wireless headphones", "www.amazon.com", 1))

    # The malformed third card (no title/asin) is skipped.
    assert len(rows) == 2

    first = rows[0]
    assert first["asin"] == "B09B8V1LZ3"
    assert first["title"].startswith("Acme Wireless")
    assert first["url"] == "https://www.amazon.com/dp/B09B8V1LZ3?ref=sr_1_1"
    assert first["price"] == 79.99
    assert first["currency"] == "USD"
    assert first["rating"] == 4.5
    assert first["review_count"] == 12431
    assert first["sponsored"] is True
    assert first["keyword"] == "wireless headphones"
    assert first["page"] == 1

    second = rows[1]
    assert second["price"] == 1299.00
    assert second["sponsored"] is False


def test_next_page_url():
    response = load_response("search.html", "https://www.amazon.com/s?k=wireless+headphones")
    assert next_page_url(response) == "https://www.amazon.com/s?k=wireless+headphones&page=2"


def test_parse_product():
    response = load_response("product.html", "https://www.amazon.com/dp/B09B8V1LZ3")
    row = parse_product(response, "www.amazon.com")
    assert row["asin"] == "B09B8V1LZ3"
    assert row["title"] == "Acme Wireless Over-Ear Headphones, 40h Battery"
    assert row["price"] == 79.99
    assert row["currency"] == "USD"
    assert row["rating"] == 4.5
    assert row["review_count"] == 12431
    assert row["image"].endswith("61abc.jpg")


def test_asin_from_url():
    assert asin_from_url("https://www.amazon.com/gp/product/B0EXAMPLE9/") == "B0EXAMPLE9"
    assert asin_from_url("https://www.amazon.com/s?k=foo") is None
