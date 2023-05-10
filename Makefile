# Project settings
PACKAGE := async_btree
PACKAGES := $(PACKAGE) tests
MODULES := $(wildcard $(PACKAGE)/*.py)

# const
.DEFAULT_GOAL := help
#FAILURES := .pytest_cache/v/cache/lastfailed
FAILURES := .cache/v/cache/lastfailed
DIST_FILES := dist/*.tar.gz dist/*.whl

GIT_COMMIT_SHA := $(shell git rev-parse HEAD)

 # MAIN TASKS ##################################################################

.PHONY: all
all: install


.PHONY: debug-info
debug-info:  ## Show poetry debug info
	poetry debug:info

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# PROJECT DEPENDENCIES ########################################################
install: .install .cache ## Install project dependencies

.install: poetry.lock
	$(MAKE) configure
	poetry install -E curio
	poetry check
	@touch $@

poetry.lock: pyproject.toml
	$(MAKE) configure
	poetry lock
	$(MAKE) requirements.txt
	@touch $@

.cache:
	@mkdir -p .cache

.PHONY: requirements.txt
requirements.txt:  ## Generate requirements.txt and requirements-dev.txt
	@poetry export --without-hashes -f requirements.txt > requirements.txt
	@sed '1d' requirements.txt
	@poetry export --without-hashes --dev -f requirements.txt > requirements-dev.txt


.PHONY: configure
configure:
	@poetry config virtualenvs.in-project true
	@poetry run python -m pip install --upgrade pip

# CHECKS ######################################################################

.PHONY: check
check: install   ## Run linters and static analysis
	poetry run isort $(PACKAGES) 
	poetry run black $(PACKAGES)
	poetry run ruff check $(PACKAGES)
	poetry run mypy --show-error-codes --config-file pyproject.toml $(PACKAGE)


# TESTS #######################################################################

.PHONY: test
test: install ## Run unit tests
	@if test -e $(FAILURES); then poetry run pytest tests --last-failed --exitfirst; fi
	@rm -rf $(FAILURES)
	poetry run pytest


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
	poetry publish
	$(MAKE) tag


.PHONY: next-patch-version
next-patch-version:  ## Increment patch version
	$(MAKE) configure
	git checkout main
	git pull
	poetry version patch
	$(MAKE) install
	git add .
	git commit -m "Next version"
	git push origin main


.PHONY: tag
tag:  ## Tags current repository
	git diff --name-only --exit-code
	@PROJECT_RELEASE=$$(poetry version | awk 'END {print $$NF}') ; \
		git tag "v$$PROJECT_RELEASE" ; \
		git push origin "v$$PROJECT_RELEASE"

.PHONY: release
release: next-patch-version publish

# DOC #########################################################################

.PHONY: build-docs
build-docs:  ## Build and publish sit documentation.
	@poetry run mkdocs build --clean


.PHONY: publish-docs
publish-docs:  ## Build and publish sit documentation.
	@poetry run mkdocs gh-deploy  --clean 


# CLEANUP #####################################################################

.PHONY: clean
clean:  ## Delete all generated and temporary files
	@rm -rf *.spec dist build .eggs *.egg-info .install .cache .coverage htmlcov .mypy_cache .pytest_cache site .ruff_cache
	@find $(PACKAGES) -type d -name '__pycache__' -exec rm -rf {} +



