#!/usr/bin/env bash
# Fetch full detail for specific ASINs and export to CSV.
#
#   export SCRAPEUNBLOCKER_KEY="your_key_here"
#   export SU_LOCAL_ROUTING=1
#   ./examples/products_to_csv.sh "B09B8V1LZ3,B0EXAMPLE9"
set -euo pipefail

ASINS="${1:-B09B8V1LZ3}"

scrapy crawl amazon_product \
  -a asins="$ASINS" \
  -O products.csv

echo "Wrote products.csv"
