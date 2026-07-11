.PHONY: validate lint format test

validate:
	@bash scripts/verify.sh

lint:
	@python -m ruff check app tests
	@python -m ruff format --check app tests

format:
	@python -m ruff format app tests

test:
	@python -m unittest discover -s tests
