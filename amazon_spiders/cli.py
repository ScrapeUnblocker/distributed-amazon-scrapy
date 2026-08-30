"""Thin convenience CLI: ``distributed-amazon`` wraps ``scrapy crawl``.

This is purely a nicety for local runs and quick exports. On Spider Cloud you
run spiders from the dashboard; nothing here is required there.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="distributed-amazon",
        description="Scrape Amazon via ScrapeUnblocker Spider Cloud (local runner).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="crawl Amazon search listings")
    search.add_argument("keyword", help="search term, or comma-separated terms")
    search.add_argument("--marketplace", default="www.amazon.com")
    search.add_argument("--pages", type=int, default=1)
    search.add_argument("--country", default=None, help="exit-IP ISO-2 country code")
    search.add_argument("-o", "--output", default=None, help="output file (.json/.csv/.jsonl)")

    product = sub.add_parser("product", help="fetch specific products by ASIN or URL")
    product.add_argument("ids", help="comma-separated ASINs or product URLs")
    product.add_argument("--marketplace", default="www.amazon.com")
    product.add_argument("--country", default=None)
    product.add_argument("-o", "--output", default=None)

    return parser


def _spider_args(args: argparse.Namespace) -> tuple[str, dict]:
    if args.command == "search":
        spider_args = {
            "keywords": args.keyword,
            "marketplace": args.marketplace,
            "pages": args.pages,
        }
        if args.country:
            spider_args["country"] = args.country
        return "amazon_search", spider_args

    ids = args.ids
    kind = "urls" if "://" in ids else "asins"
    spider_args = {kind: ids, "marketplace": args.marketplace}
    if args.country:
        spider_args["country"] = args.country
    return "amazon_product", spider_args


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Imported lazily so `--help` and tests don't spin up Twisted.
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    spider_name, spider_args = _spider_args(args)

    settings = get_project_settings()
    if args.output:
        settings.set("FEEDS", {args.output: {"format": _fmt(args.output)}})

    process = CrawlerProcess(settings)
    process.crawl(spider_name, **spider_args)
    process.start()
    return 0


def _fmt(path: str) -> str:
    lowered = path.lower()
    if lowered.endswith(".csv"):
        return "csv"
    if lowered.endswith(".jsonl") or lowered.endswith(".jl"):
        return "jsonlines"
    return "json"


if __name__ == "__main__":
    sys.exit(main())
