# const
.DEFAULT_GOAL := help

# MAIN TASKS ##################################################################

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# PROJECT DEPENDENCIES ########################################################

.PHONY: install
install: configure .cache ## Install project dependencies
	$(MAKE) configure
	poetry lock
	poetry install --with docs --extras "curio"
	poetry check


poetry.lock: pyproject.toml
	$(MAKE) configure
	poetry lock
	@touch $@

.cache:
	@mkdir -p .cache

.PHONY: configure
configure:
	@poetry config virtualenvs.in-project true
	@poetry run python -m pip install --upgrade pip
	@poetry run python -m pip install --upgrade setuptools

# git util #####################################################################

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
