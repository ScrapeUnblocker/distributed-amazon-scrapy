# distributed-amazon-scrapy

[![CI](https://github.com/ScrapeUnblocker/distributed-amazon-scrapy/actions/workflows/ci.yml/badge.svg)](https://github.com/ScrapeUnblocker/distributed-amazon-scrapy/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-shaped **Scrapy** project that scrapes Amazon search listings and
product pages **at scale** on
[ScrapeUnblocker **Spider Cloud**](https://developers.scrapeunblocker.com/spider-cloud/?utm_source=github&utm_medium=integration&utm_campaign=example-repos)
— deploy and run in minutes.

> **Powered by [ScrapeUnblocker](https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos).**
> Amazon blocks datacenter traffic aggressively. ScrapeUnblocker handles the
> unblocking, IP rotation and rendering so your spiders just get clean HTML.

## How it works

Every request is marked with `meta={"unblock": True}`. On Spider Cloud that flag
routes the request through ScrapeUnblocker **automatically** — the project needs
no SDK, no base class and no config. For local development, a bundled downloader
middleware reproduces the exact same routing by calling the public
[`getPageSource`](https://developers.scrapeunblocker.com/guides/page-source?utm_source=github&utm_medium=integration&utm_campaign=example-repos)
endpoint, so the same spiders run identically on your laptop and in the cloud.

```
spider  ──►  meta={"unblock": True}  ──►  ScrapeUnblocker  ──►  amazon.com
                                          (auto on Spider Cloud,
                                           getPageSource locally)
```

## Features

- **Two spiders** — `amazon_search` (paginated listings) and `amazon_product`
  (detail by ASIN or URL).
- **Runs anywhere unchanged** — identical code locally and on Spider Cloud.
- **Clean, typed items** — ASIN, title, URL, image, price + currency, rating,
  review count, sponsored flag.
- **Robust price parsing** — handles `$1,299.00` and `1.299,00 EUR` alike.
- **Any Amazon marketplace** and optional `--country` exit IP.
- **Export to JSON / CSV / JSONL** via Scrapy feed exports.
- **Offline unit tests** — parsing, routing and CLI are tested with fixtures and
  mocks; no API credit spent in CI.

## Install

```bash
git clone https://github.com/ScrapeUnblocker/distributed-amazon-scrapy.git
cd distributed-amazon-scrapy
pip install -e ".[dev]"     # or: pip install -r requirements.txt
```

## Run locally

Get an API key from your
[ScrapeUnblocker dashboard](https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos)
and enable local routing:

```bash
cp .env.example .env        # then edit it, or just export the two vars:
export SCRAPEUNBLOCKER_KEY="your_key_here"
export SU_LOCAL_ROUTING=1
```

### With `scrapy crawl`

```bash
# Search listings -> JSON
scrapy crawl amazon_search -a keyword="wireless headphones" -a pages=2 -O products.json

# Multiple keywords, a non-US marketplace, and a country exit IP
scrapy crawl amazon_search \
  -a keywords="running shoes,trail shoes" \
  -a marketplace="www.amazon.co.uk" \
  -a country="gb" \
  -O uk.json

# Product detail by ASIN -> CSV
scrapy crawl amazon_product -a asins="B09B8V1LZ3,B0EXAMPLE9" -O products.csv
```

### With the convenience CLI

`pip install` also exposes a `distributed-amazon` command:

```bash
distributed-amazon search "wireless headphones" --pages 2 -o products.json
distributed-amazon product "B09B8V1LZ3" -o product.json
```

### As a library

```python
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
process.crawl("amazon_search", keyword="wireless headphones", pages=2)
process.start()
```

## Example output

```json
{
  "asin": "B09B8V1LZ3",
  "title": "Acme Wireless Over-Ear Headphones, 40h Battery",
  "url": "https://www.amazon.com/dp/B09B8V1LZ3",
  "image": "https://m.media-amazon.com/images/I/61abc.jpg",
  "price": 79.99,
  "currency": "USD",
  "price_raw": "$79.99",
  "rating": 4.5,
  "review_count": 12431,
  "sponsored": false,
  "marketplace": "www.amazon.com",
  "keyword": "wireless headphones",
  "page": 1
}
```

## Deploy to Spider Cloud

The same project runs at scale on Spider Cloud with a schedule and automatic
routing. See [`examples/deploy_to_spider_cloud.md`](examples/deploy_to_spider_cloud.md):

```bash
pip install scrapeunblocker-cloud
su-cloud login
su-cloud deploy
```

## Project layout

```
distributed-amazon-scrapy/
├── scrapy.cfg                     # Spider Cloud entry point
├── amazon_spiders/
│   ├── settings.py                # Scrapy + routing settings
│   ├── items.py                   # ProductItem
│   ├── middlewares.py             # local ScrapeUnblocker routing
│   ├── pipelines.py               # price normalisation
│   ├── parsers.py                 # pure HTML -> dict (unit-tested)
│   ├── prices.py                  # currency/amount parsing
│   ├── cli.py                     # `distributed-amazon` command
│   └── spiders/
│       ├── amazon_search.py
│       └── amazon_product.py
├── examples/
├── tests/                         # offline, mocked
├── pyproject.toml
├── requirements.txt
├── Makefile
└── .github/workflows/ci.yml
```

## Development

```bash
make install     # editable install with dev extras
make lint        # ruff check + format check
make test        # pytest (offline, no API credit)
make run         # example crawl (needs the two env vars)
```

## Notes & etiquette

- Scrape responsibly and respect Amazon's Terms of Service and applicable law.
- Selectors track Amazon's public layout and may need occasional updates — the
  parsing logic is isolated in `parsers.py` and covered by tests to make that easy.
- No invented benchmarks here; throughput depends on your plan and target.

## Links

- Website — https://scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos
- Docs — https://developers.scrapeunblocker.com/?utm_source=github&utm_medium=integration&utm_campaign=example-repos
- Spider Cloud — https://developers.scrapeunblocker.com/spider-cloud/?utm_source=github&utm_medium=integration&utm_campaign=example-repos
- getPageSource guide — https://developers.scrapeunblocker.com/guides/page-source?utm_source=github&utm_medium=integration&utm_campaign=example-repos

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 ScrapeUnblocker.
