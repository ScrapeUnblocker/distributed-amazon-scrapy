from urllib.parse import parse_qs, urlparse

import pytest
import scrapy
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from scrapy.settings import Settings
from scrapy.signalmanager import SignalManager

from amazon_spiders.middlewares import ScrapeUnblockerMiddleware


class _FakeCrawler:
    """Minimal crawler stub - ``from_crawler`` only needs ``settings`` and ``signals``.

    Avoids ``scrapy.utils.test.get_crawler``, which on Scrapy >= 2.13 requires an
    installed Twisted reactor and raises ``RuntimeError`` under a plain pytest run.
    """

    def __init__(self, settings_dict=None):
        self.settings = Settings(settings_dict or {})
        self.signals = SignalManager(self)


def _mw(enabled=True, key="testkey"):
    return ScrapeUnblockerMiddleware(
        api_base="https://api.scrapeunblocker.com", api_key=key, enabled=enabled
    )


def test_routes_marked_request_through_getpagesource():
    mw = _mw()
    req = scrapy.Request(
        "https://www.amazon.com/s?k=headphones",
        meta={"unblock": True, "su_proxy_country": "us"},
    )
    routed = mw.process_request(req, spider=None)

    assert routed is not None
    parsed = urlparse(routed.url)
    assert parsed.path == "/getPageSource"
    assert routed.method == "POST"
    assert routed.body == b""
    assert routed.headers.get("x-scrapeunblocker-key") == b"testkey"

    qs = parse_qs(parsed.query)
    assert qs["url"] == ["https://www.amazon.com/s?k=headphones"]
    assert qs["proxy_country"] == ["us"]
    assert routed.meta["_su_orig_url"] == "https://www.amazon.com/s?k=headphones"


def test_already_routed_request_passes_through():
    mw = _mw()
    req = scrapy.Request("https://api.scrapeunblocker.com/getPageSource", meta={"_su_routed": True})
    assert mw.process_request(req, spider=None) is None


def test_unmarked_request_passes_through():
    mw = _mw()
    req = scrapy.Request("https://www.amazon.com/robots.txt")
    assert mw.process_request(req, spider=None) is None


def test_disabled_is_noop():
    mw = _mw(enabled=False)
    req = scrapy.Request("https://www.amazon.com/s?k=x", meta={"unblock": True})
    assert mw.process_request(req, spider=None) is None


def test_process_response_restores_original_url():
    mw = _mw()
    req = scrapy.Request(
        "https://api.scrapeunblocker.com/getPageSource",
        meta={"_su_routed": True, "_su_orig_url": "https://www.amazon.com/dp/B09B8V1LZ3"},
    )
    resp = HtmlResponse(url=req.url, body=b"<html></html>", encoding="utf-8", request=req)
    restored = mw.process_response(req, resp, spider=None)
    assert restored.url == "https://www.amazon.com/dp/B09B8V1LZ3"


def test_from_crawler_requires_key_when_enabled(monkeypatch):
    monkeypatch.delenv("SCRAPEUNBLOCKER_KEY", raising=False)
    crawler = _FakeCrawler({"SU_LOCAL_ROUTING": True})
    with pytest.raises(NotConfigured):
        ScrapeUnblockerMiddleware.from_crawler(crawler)
