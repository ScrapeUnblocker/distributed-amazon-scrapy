"""Shared test helpers."""

from __future__ import annotations

from pathlib import Path

from scrapy.http import HtmlResponse, Request

FIXTURES = Path(__file__).parent / "fixtures"


def load_response(name: str, url: str) -> HtmlResponse:
    """Build a Scrapy HtmlResponse from a saved fixture - no network involved."""
    body = (FIXTURES / name).read_bytes()
    return HtmlResponse(url=url, body=body, encoding="utf-8", request=Request(url))
