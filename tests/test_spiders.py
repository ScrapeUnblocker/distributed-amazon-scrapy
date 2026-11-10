import asyncio

from amazon_spiders.spiders.amazon_product import AmazonProductSpider
from amazon_spiders.spiders.amazon_search import AmazonSearchSpider


def _start(spider):
    async def collect():
        return [request async for request in spider.start()]

    return asyncio.run(collect())


def test_search_start_yields_routed_requests():
    spider = AmazonSearchSpider(keywords="running shoes,trail shoes", country="gb")
    requests = _start(spider)

    assert [r.url for r in requests] == [
        "https://www.amazon.com/s?k=running+shoes&page=1",
        "https://www.amazon.com/s?k=trail+shoes&page=1",
    ]
    for request in requests:
        assert request.meta["unblock"] is True
        assert request.meta["su_proxy_country"] == "gb"
        assert request.meta["page"] == 1


def test_product_start_yields_routed_requests():
    spider = AmazonProductSpider(asins="B09B8V1LZ3", urls="https://www.amazon.co.uk/dp/B0EXAMPLE9")
    requests = _start(spider)

    assert [r.url for r in requests] == [
        "https://www.amazon.com/dp/B09B8V1LZ3",
        "https://www.amazon.co.uk/dp/B0EXAMPLE9",
    ]
    assert all(r.meta["unblock"] is True for r in requests)
