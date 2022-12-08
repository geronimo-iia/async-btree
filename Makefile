# Project settings
PACKAGE := async_btree
PACKAGES := $(PACKAGE) tests
MODULES := $(wildcard $(PACKAGE)/*.py)

# const
.DEFAULT_GOAL := help
#FAILURES := .pytest_cache/v/cache/lastfailed
FAILURES := .cache/v/cache/lastfailed
DIST_FILES := dist/*.tar.gz dist/*.whl

 # MAIN TASKS ##################################################################

.PHONY: all
all: install

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# PROJECT DEPENDENCIES ########################################################

.PHONY: install
install: .install .cache ## Install project dependencies

.install: poetry.lock
	$(MAKE) configure
	poetry install -E curio
	poetry check
	@touch $@

poetry.lock: pyproject.toml
	$(MAKE) configure
	poetry lock
	poetry export --without-hashes -f requirements.txt > requirements.txt
	@touch $@

.cache:
	@mkdir -p .cache

.PHONY: configure
configure: 
	@poetry config virtualenvs.create true
	@poetry config virtualenvs.in-project true
	@poetry config virtualenvs.path .venv
	@poetry run python -m pip install --upgrade pip


# CHECKS ######################################################################

.PHONY: check
check: install   ## Run linters and static analysis
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES)
	poetry run flakehell lint $(PACKAGE)
	poetry run mypy $(PACKAGE)

# TESTS #######################################################################

.PHONY: test
test: install ## Run unit tests
	@if test -e $(FAILURES); then poetry run pytest tests --last-failed --exitfirst; fi
	@rm -rf $(FAILURES)
	poetry run pytest tests -o log_cli=true -o log_cli_level=INFO


# BUILD #######################################################################

.PHONY: build
build: install check test $(DIST_FILES) ## Builds the source and wheels archives
$(DIST_FILES): $(MODULES) pyproject.toml
	@rm -f $(DIST_FILES)
	poetry build

# RELEASE #####################################################################

.PHONY: publish
publish: build ## Publishes the package, previously built with the build command, to the remote repository
	$(MAKE) configure
	poetry publish -r datalab
	$(MAKE) tag

.PHONY: tag
tag:  ## Tags current repository
	git diff --name-only --exit-code
	@PROJECT_RELEASE=$$(poetry version | awk 'END {print $$NF}') ; \
		git tag "v$$PROJECT_RELEASE" ; \
		git push origin "v$$PROJECT_RELEASE"

.PHONY: next-version
next-version:  ## Increment patch version
	$(MAKE) configure
	git checkout main
	git pull
	poetry version patch
	$(MAKE) install
	git add .
	git commit -m "Next version"
	git push origin main

# DOC #########################################################################

SPHINX_BUILD_DIR = .cache/sphinx
.PHONY: docs
docs:  ## Build and publish sit documentation.
	@rm -rf docs/
	@rm -rf $(SPHINX_BUILD_DIR)/
	@mkdir -p $(SPHINX_BUILD_DIR)
	@poetry run sphinx-build -M html "sphinx" "$(SPHINX_BUILD_DIR)"
	@mv $(SPHINX_BUILD_DIR)/html docs/
	@touch docs/.nojekyll


# CLEANUP #####################################################################

.PHONY: clean
clean:  ## Delete all generated and temporary files
	@rm -rf *.spec dist build .eggs *.egg-info .install .cache .coverage htmlcov .mypy_cache .pytest_cache  .pytest 
	@find $(PACKAGES) -type d -name '__pycache__' -exec rm -rf {} +

