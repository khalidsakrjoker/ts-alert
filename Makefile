.PHONY: setup dev lint format format-check typecheck test coverage build audit secrets up down ci

setup: ## install package and development dependencies
	python -m pip install -e ".[dev]"
	@command -v pre-commit >/dev/null 2>&1 && pre-commit install || true

dev: ## run a short import smoke check
	python -c "import ts_alert; print(ts_alert.__version__)"

lint: ## run ruff linter
	ruff check src tests

format: ## format code with ruff
	ruff format src tests

format-check: ## check formatting without writing
	ruff format --check src tests

typecheck: ## run mypy in strict mode
	mypy

test: ## run unit and integration tests
	pytest

coverage: ## run tests with coverage gate
	pytest --cov=ts_alert --cov-report=term-missing --cov-fail-under=80

build: ## build distribution packages
	python -m pip install --upgrade build
	python -m build

audit: ## scan dependencies for known vulnerabilities
	python -m pip install --upgrade pip-audit
	pip-audit

secrets: ## scan the working tree for secrets
	gitleaks detect --source . --redact

up: ## start local services
	docker compose up --build -d

down: ## stop local services
	docker compose down

ci: format-check lint typecheck coverage build audit ## run local CI sequence
