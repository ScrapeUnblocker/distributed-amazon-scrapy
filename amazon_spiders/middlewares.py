"""Local ScrapeUnblocker routing for Scrapy.

On Spider Cloud, a request marked ``meta={"unblock": True}`` is routed through
ScrapeUnblocker by the platform - the project needs no changes. This downloader
middleware reproduces that behaviour for **local** runs so you can develop and
test the exact same spiders on your machine.

Enable it locally with::

    export SCRAPEUNBLOCKER_KEY="your_key_here"
    export SU_LOCAL_ROUTING=1

When ``SU_LOCAL_ROUTING`` is off (the default, and how it runs on Spider Cloud)
the middleware is a no-op passthrough.

It works by rewriting an outgoing request to the public ``getPageSource``
endpoint (query-string parameters, ``x-scrapeunblocker-key`` header) and then
restoring the original URL on the response so the spider's selectors and
``response.urljoin`` keep working unchanged.

Docs: https://docs.scrapeunblocker.com/guides/page-source?utm_source=github&utm_medium=integration&utm_campaign=example-repos
"""

from __future__ import annotations

import os
from urllib.parse import urlencode

from scrapy import signals
from scrapy.exceptions import NotConfigured

# meta keys the caller may set; each maps to a getPageSource query parameter.
_META_TO_PARAM = {
    "su_proxy_country": "proxy_country",
    "su_time_sleep": "time_sleep",
    "su_parsed_data": "parsed_data",
    "su_list_elements": "list_elements",
    "su_method": "method",
    "su_value": "value",
}

_ROUTED_FLAG = "_su_routed"
_ORIG_URL = "_su_orig_url"


class ScrapeUnblockerMiddleware:
    """Route ``meta["unblock"]`` requests through getPageSource during local runs."""

    def __init__(self, api_base: str, api_key: str | None, enabled: bool):
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.enabled = enabled

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        enabled = settings.getbool("SU_LOCAL_ROUTING")
        api_key = os.environ.get("SCRAPEUNBLOCKER_KEY")
        if enabled and not api_key:
            raise NotConfigured(
                "SU_LOCAL_ROUTING is on but SCRAPEUNBLOCKER_KEY is not set. "
                "Get a key at https://scrapeunblocker.com/"
                "?utm_source=github&utm_medium=integration&utm_campaign=example-repos"
            )
        mw = cls(
            api_base=settings.get("SU_API_BASE", "https://api.scrapeunblocker.com"),
            api_key=api_key,
            enabled=enabled,
        )
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        return mw

    def spider_opened(self, spider):
        if self.enabled:
            spider.logger.info("ScrapeUnblocker local routing is ON (getPageSource).")
        else:
            spider.logger.info(
                "ScrapeUnblocker local routing is OFF - requests go direct. "
                "On Spider Cloud, meta['unblock'] requests are routed automatically."
            )

    def process_request(self, request, spider):
        if not self.enabled or request.meta.get(_ROUTED_FLAG):
            return None
        if not request.meta.get("unblock"):
            return None

        params = {"url": request.url}
        for meta_key, param in _META_TO_PARAM.items():
            value = request.meta.get(meta_key)
            if value is not None:
                params[param] = str(value).lower() if isinstance(value, bool) else value

        api_url = f"{self.api_base}/getPageSource?{urlencode(params)}"
        headers = {"x-scrapeunblocker-key": self.api_key}

        meta = dict(request.meta)
        meta[_ROUTED_FLAG] = True
        meta[_ORIG_URL] = request.url
        # POST with an empty body, exactly like Spider Cloud routing does.
        return request.replace(url=api_url, method="POST", body=b"", headers=headers, meta=meta)

    def process_response(self, request, response, spider):
        if request.meta.get(_ROUTED_FLAG):
            # Restore the original URL so selectors and urljoin behave normally.
            return response.replace(url=request.meta[_ORIG_URL])
        return response
