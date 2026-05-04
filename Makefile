# const
.DEFAULT_GOAL := help

# HELP #########################################################################

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# PROJECT DEPENDENCIES ########################################################

.PHONY: install
install: lock ## Install project dependencies (asyncio only)
	uv sync

.PHONY: install-curio
install-curio: lock ## Install project dependencies with curio
	uv sync --group curio

.PHONY: lock
lock: pyproject.toml #codeartifact-index
	uv lock

# CODE QUALITY #################################################################

.PHONY: lint
lint: ## Check format, linting and types
	uv run ruff format --check .
	uv run ruff check .
	uv run pyright

.PHONY: lint-fix
lint-fix: ## Fix all auto-fixable issues
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: test
test: ## Run unit tests
	uv run pytest

.PHONY: check
check: lint test ## Run all checks on the code base

# BUILD ########################################################################

.PHONY: build
build: check ## Build module
	uv build

.PHONY: publish
publish: build ## Publish module
	uv publish

# DOCS #########################################################################

.PHONY: docs
docs: ## Build site documentation
	git fetch origin gh-pages
	uv run mkdocs build --clean

.PHONY: docs-publish
docs-publish: ## Publish site documentation
	uv run mkdocs gh-deploy --clean

# MAINTENANCE ##################################################################

.PHONY: clean
clean: ## Remove all generated and temporary files
	uv cache clean
	rm -rf *.spec dist build .eggs *.egg-info .install .cache .coverage htmlcov .mypy_cache .pytest_cache site .ruff_cache .venv
	find async_btree tests -type d -name '__pycache__' -exec rm -rf {} +

.PHONY: requirements
requirements: ## Generate requirements.txt
	uv pip compile pyproject.toml -o requirements.txt

