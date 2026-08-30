.PHONY: install lint format test run clean

install:
	pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

test:
	pytest -q

# Example local run. Requires SCRAPEUNBLOCKER_KEY and SU_LOCAL_ROUTING=1.
run:
	scrapy crawl amazon_search -a keyword="wireless headphones" -a pages=1 -O out.json

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache __pycache__ out.json out.csv
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
