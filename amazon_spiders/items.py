"""Typed items produced by the spiders."""

import scrapy


class ProductItem(scrapy.Item):
    """A single Amazon product, from search listings or a product page."""

    asin = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    price = scrapy.Field()  # float or None
    currency = scrapy.Field()  # ISO-ish code / symbol, or None
    price_raw = scrapy.Field()  # original text, kept for auditing
    rating = scrapy.Field()  # float (stars) or None
    review_count = scrapy.Field()  # int or None
    sponsored = scrapy.Field()  # bool
    marketplace = scrapy.Field()
    keyword = scrapy.Field()  # search term, when from a listing
    page = scrapy.Field()  # search page number, when from a listing
