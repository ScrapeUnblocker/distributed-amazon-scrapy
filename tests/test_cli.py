import pytest

from amazon_spiders.cli import _fmt, _spider_args, build_parser


def test_search_args():
    args = build_parser().parse_args(["search", "wireless headphones", "--pages", "3"])
    spider, kwargs = _spider_args(args)
    assert spider == "amazon_search"
    assert kwargs["keywords"] == "wireless headphones"
    assert kwargs["pages"] == 3


def test_product_detects_urls_vs_asins():
    args = build_parser().parse_args(["product", "B09B8V1LZ3,B0EXAMPLE9"])
    spider, kwargs = _spider_args(args)
    assert spider == "amazon_product"
    assert "asins" in kwargs and "urls" not in kwargs

    args = build_parser().parse_args(["product", "https://www.amazon.com/dp/B09B8V1LZ3"])
    _, kwargs = _spider_args(args)
    assert "urls" in kwargs and "asins" not in kwargs


def test_country_passthrough():
    args = build_parser().parse_args(["search", "shoes", "--country", "de"])
    _, kwargs = _spider_args(args)
    assert kwargs["country"] == "de"


def test_output_format_detection():
    assert _fmt("out.csv") == "csv"
    assert _fmt("out.jsonl") == "jsonlines"
    assert _fmt("out.json") == "json"
    assert _fmt("out.unknown") == "json"


def test_missing_command_errors():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
