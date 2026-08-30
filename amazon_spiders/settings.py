"""Scrapy settings for the amazon_spiders project.

Only public, portable Scrapy knobs live here. The ScrapeUnblocker routing itself
is controlled per-request via ``meta["unblock"]`` (see the spiders) and, for local
runs, by :class:`amazon_spiders.middlewares.ScrapeUnblockerMiddleware`.
"""

from __future__ import annotations

import os

BOT_NAME = "amazon_spiders"

SPIDER_MODULES = ["amazon_spiders.spiders"]
NEWSPIDER_MODULE = "amazon_spiders.spiders"

# --- ScrapeUnblocker routing -------------------------------------------------
# Base URL of the public API. Override only if you have a dedicated endpoint.
SU_API_BASE = os.environ.get("SU_API_BASE", "https://api.scrapeunblocker.com")

# On Spider Cloud, requests marked ``meta["unblock"]`` are routed for you, so the
# local middleware stays out of the way. For local development set
# ``SU_LOCAL_ROUTING=1`` (and ``SCRAPEUNBLOCKER_KEY``) to reproduce that routing
# by calling getPageSource directly.
SU_LOCAL_ROUTING = os.environ.get("SU_LOCAL_ROUTING", "").lower() in {"1", "true", "yes"}

DOWNLOADER_MIDDLEWARES = {
    # Sits close to the downloader so retries/robots run against the real target.
    "amazon_spiders.middlewares.ScrapeUnblockerMiddleware": 543,
}

ITEM_PIPELINES = {
    "amazon_spiders.pipelines.PriceNormalizePipeline": 300,
}

# --- Polite, portable crawl defaults ----------------------------------------
# ScrapeUnblocker manages IPs and blocking, so a modest concurrency is plenty.
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 8
DOWNLOAD_TIMEOUT = 90
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504]
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
}

# Feed export niceties for CLI runs (`-O out.json` / `-O out.csv`).
FEED_EXPORT_ENCODING = "utf-8"

# Scrapy 2.x forward-compat defaults.
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
