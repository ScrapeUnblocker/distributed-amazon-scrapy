"""Spider: fetch full detail for specific Amazon products.

Give it ASINs or full product URLs::

    scrapy crawl amazon_product -a asins="B09B8V1LZ3,B0Bshtml" -O products.json
    scrapy crawl amazon_product -a urls="https://www.amazon.com/dp/B09B8V1LZ3" -O products.csv
"""

from __future__ import annotations

import scrapy

from amazon_spiders.items import ProductItem
from amazon_spiders.parsers import parse_product


class AmazonProductSpider(scrapy.Spider):
    name = "amazon_product"

    def __init__(
        self,
        asins: str | None = None,
        urls: str | None = None,
        marketplace: str = "www.amazon.com",
        country: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.marketplace = marketplace
        self.country = country

        self.start_urls: list[str] = []
        for asin in (asins or "").split(","):
            asin = asin.strip()
            if asin:
                self.start_urls.append(f"https://{marketplace}/dp/{asin}")
        for url in (urls or "").split(","):
            url = url.strip()
            if url:
                self.start_urls.append(url)
        if not self.start_urls:
            raise ValueError("Provide -a asins='A,B' or -a urls='https://...'")

    def start_requests(self):
        for url in self.start_urls:
            meta = {"unblock": True}
            if self.country:
                meta["su_proxy_country"] = self.country
            yield scrapy.Request(url, callback=self.parse, meta=meta, dont_filter=True)

    def parse(self, response):
        row = parse_product(response, self.marketplace)
        if row.get("title"):
            yield ProductItem(**row)
        else:
            self.logger.warning("No product title parsed from %s", response.url)
