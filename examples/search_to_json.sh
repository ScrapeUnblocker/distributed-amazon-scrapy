#!/usr/bin/env bash
# Scrape 2 pages of Amazon search results to JSON.
#
#   export SCRAPEUNBLOCKER_KEY="your_key_here"
#   export SU_LOCAL_ROUTING=1
#   ./examples/search_to_json.sh "wireless headphones"
set -euo pipefail

KEYWORD="${1:-wireless headphones}"

scrapy crawl amazon_search \
  -a keyword="$KEYWORD" \
  -a pages=2 \
  -O products.json

echo "Wrote products.json"
