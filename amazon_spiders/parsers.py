"""Pure HTML -> item parsing.

Kept separate from the spiders so the extraction logic can be unit-tested
offline against saved fixtures, with no network and no API credit spent.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from urllib.parse import urljoin

from amazon_spiders.prices import parse_price

_ASIN_IN_URL = re.compile(r"/(?:dp|gp/product)/([A-Z0-9]{10})")
_INT_RE = re.compile(r"[\d,.]+")


def _first(selectors_result) -> str | None:
    value = selectors_result.get()
    if value is None:
        return None
    value = value.strip()
    return value or None


def _to_int(text: str | None) -> int | None:
    if not text:
        return None
    match = _INT_RE.search(text)
    if not match:
        return None
    digits = re.sub(r"[.,]", "", match.group(0))
    return int(digits) if digits.isdigit() else None


def _to_float(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"\d+(?:[.,]\d+)?", text)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def asin_from_url(url: str | None) -> str | None:
    """Pull the 10-char ASIN out of a product URL, if present."""
    if not url:
        return None
    match = _ASIN_IN_URL.search(url)
    return match.group(1) if match else None


def parse_search(response, keyword: str, marketplace: str, page: int) -> Iterator[dict]:
    """Yield product dicts from an Amazon search results page.

    Selectors use several fallbacks because Amazon ships small layout variants.
    Items without a title or ASIN are skipped rather than emitted half-empty.
    """
    cards = response.css("div.s-result-item[data-asin], div[data-component-type='s-search-result']")
    for card in cards:
        asin = card.attrib.get("data-asin") or ""
        asin = asin.strip() or None

        title = _first(card.css("h2 a span::text")) or _first(card.css("h2 span::text"))

        href = _first(card.css("h2 a::attr(href)")) or _first(
            card.css("a.a-link-normal.s-no-outline::attr(href)")
        )
        url = urljoin(response.url, href) if href else None
        if asin is None:
            asin = asin_from_url(url)

        if not title or not asin:
            continue

        price_raw = _first(card.css("span.a-price span.a-offscreen::text"))
        amount, currency = parse_price(price_raw)

        rating = _to_float(_first(card.css("span.a-icon-alt::text")))
        review_count = _to_int(
            _first(card.css("span[aria-label] span.a-size-base::text"))
            or _first(card.css("span.s-underline-text::text"))
        )
        image = _first(card.css("img.s-image::attr(src)"))
        sponsored = bool(card.css("span.s-sponsored-label-text, span.puis-sponsored-label-text"))

        yield {
            "asin": asin,
            "title": title,
            "url": url,
            "image": image,
            "price": amount,
            "currency": currency,
            "price_raw": price_raw,
            "rating": rating,
            "review_count": review_count,
            "sponsored": sponsored,
            "marketplace": marketplace,
            "keyword": keyword,
            "page": page,
        }


def next_page_url(response) -> str | None:
    """Absolute URL of the 'Next' pagination link, if any."""
    href = _first(response.css("a.s-pagination-next::attr(href)"))
    if not href or "s-pagination-disabled" in (
        response.css("a.s-pagination-next::attr(class)").get() or ""
    ):
        return None
    return urljoin(response.url, href)


def parse_product(response, marketplace: str) -> dict:
    """Extract a single product's detail from its page."""
    title = _first(response.css("#productTitle::text"))
    price_raw = (
        _first(response.css("#corePrice_feature_div span.a-offscreen::text"))
        or _first(response.css("span.a-price span.a-offscreen::text"))
        or _first(response.css("#priceblock_ourprice::text"))
    )
    amount, currency = parse_price(price_raw)
    rating = _to_float(_first(response.css("span[data-hook='rating-out-of-text']::text")))
    if rating is None:
        rating = _to_float(_first(response.css("#acrPopover span.a-icon-alt::text")))
    review_count = _to_int(_first(response.css("#acrCustomerReviewText::text")))
    image = _first(response.css("#landingImage::attr(src)")) or _first(
        response.css("#imgTagWrapperId img::attr(src)")
    )

    return {
        "asin": asin_from_url(response.url),
        "title": title,
        "url": response.url,
        "image": image,
        "price": amount,
        "currency": currency,
        "price_raw": price_raw,
        "rating": rating,
        "review_count": review_count,
        "sponsored": False,
        "marketplace": marketplace,
    }
