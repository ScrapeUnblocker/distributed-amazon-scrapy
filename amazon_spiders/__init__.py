"""distributed-amazon-scrapy.

A Scrapy project that scrapes Amazon at scale on ScrapeUnblocker Spider Cloud.

Requests marked with ``meta={"unblock": True}`` are routed through
ScrapeUnblocker automatically when the project runs on Spider Cloud. For local
development the bundled :class:`~amazon_spiders.middlewares.ScrapeUnblockerMiddleware`
reproduces that routing by calling the public ``getPageSource`` endpoint, so the
same spiders run identically on your laptop and in the cloud.

Docs: https://docs.scrapeunblocker.com/spider-cloud/?utm_source=github&utm_medium=integration&utm_campaign=example-repos
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
