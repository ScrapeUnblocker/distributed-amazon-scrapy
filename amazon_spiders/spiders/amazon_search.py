"""Spider: crawl Amazon search listings for one or more keywords.

Run on Spider Cloud, or locally with routing enabled::

    scrapy crawl amazon_search -a keyword="wireless headphones" -a pages=2 -O out.json

Every request is marked ``meta={"unblock": True}`` so it routes through
ScrapeUnblocker (automatic on Spider Cloud; via getPageSource locally).
"""

from __future__ import annotations

from urllib.parse import quote_plus

import scrapy

from amazon_spiders.items import ProductItem
from amazon_spiders.parsers import next_page_url, parse_search


class AmazonSearchSpider(scrapy.Spider):
    name = "amazon_search"

    def __init__(
        self,
        keyword: str | None = None,
        keywords: str | None = None,
        marketplace: str = "www.amazon.com",
        pages: str | int = 1,
        country: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        raw = keywords or keyword or ""
        self.keywords = [k.strip() for k in raw.split(",") if k.strip()]
        if not self.keywords:
            raise ValueError("Provide -a keyword='...' or -a keywords='a,b,c'")
        self.marketplace = marketplace
        self.max_pages = max(1, int(pages))
        self.country = country

    def _search_url(self, keyword: str, page: int) -> str:
        return f"https://{self.marketplace}/s?k={quote_plus(keyword)}&page={page}"

    def start_requests(self):
        for keyword in self.keywords:
            yield self._make_request(keyword, page=1)

    def _make_request(self, keyword: str, page: int) -> scrapy.Request:
        meta = {"unblock": True, "keyword": keyword, "page": page}
        if self.country:
            meta["su_proxy_country"] = self.country
        return scrapy.Request(
            self._search_url(keyword, page),
            callback=self.parse,
            meta=meta,
            dont_filter=True,
        )

    def parse(self, response):
        keyword = response.meta["keyword"]
        page = response.meta["page"]

        count = 0
        for row in parse_search(response, keyword, self.marketplace, page):
            count += 1
            yield ProductItem(**row)

        self.logger.info("keyword=%r page=%s -> %s products", keyword, page, count)

        if page < self.max_pages and count and next_page_url(response):
            yield self._make_request(keyword, page + 1)
