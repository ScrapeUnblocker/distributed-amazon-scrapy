"""Item pipelines."""

from __future__ import annotations

from itemadapter import ItemAdapter

from amazon_spiders.prices import parse_price


class PriceNormalizePipeline:
    """Fill ``price``/``currency`` from ``price_raw`` when the spider left them blank."""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        raw = adapter.get("price_raw")
        if raw and adapter.get("price") is None:
            amount, currency = parse_price(raw)
            adapter["price"] = amount
            if currency and not adapter.get("currency"):
                adapter["currency"] = currency
        return item
