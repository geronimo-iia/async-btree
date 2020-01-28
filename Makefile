# Project settings
PROJECT := async-btree
PACKAGE := async_btree
REPOSITORY := geronimo-iia/async-btree

# Project paths
PACKAGES := $(PACKAGE) tests
CONFIG := $(wildcard *.py)
MODULES := $(wildcard $(PACKAGE)/*.py)

# POETRY CMD
RUN := poetry run

# MAIN TASKS ##################################################################

.PHONY: all
all: install

.PHONY: ci
ci: check test ## Run all tasks that determine CI status

.PHONY: watch
watch: install .clean-test ## Continuously run all CI tasks when files chanage
	$(RUN) sniffer

# SYSTEM DEPENDENCIES #########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

.PHONY: debug-info
debug-info:  ## Show poetry debug info
	poetry debug:info

# PROJECT DEPENDENCIES ########################################################

install: .install .cache ## Install project dependencies

.install: poetry.lock 
	poetry install
	poetry install -E curio
	@ touch $@

poetry.lock: pyproject.toml
	poetry lock

.cache:
	@ mkdir -p .cache

# CHECKS ######################################################################

.PHONY: check
check: isort black flake mypy pydocstyle ## Run linters and static analysis

.PHONY: isort
isort: install
	$(RUN) isort $(PACKAGES) --recursive --apply

.PHONY: black
black: install
	$(RUN) black $(PACKAGES) 

.PHONY: mypy
mypy: install
	$(RUN) mypy $(PACKAGE)  --config-file=.mypy.ini

.PHONY: pydocstyle
pydocstyle: install
	$(RUN) pydocstyle $(PACKAGES) $(CONFIG)

.PHONY: flake
flake: install
	$(RUN) flake8 $(PACKAGES)

# TESTS #######################################################################

RANDOM_SEED ?= $(shell date +%s)
FAILURES := .cache/v/cache/lastfailed

PYTEST_OPTIONS := --random --random-seed=$(RANDOM_SEED)
ifdef DISABLE_COVERAGE
PYTEST_OPTIONS += --no-cov --disable-warnings
endif
PYTEST_RERUN_OPTIONS := --last-failed --exitfirst

.PHONY: test
test: install ## Run unit tests
	@ if test -e $(FAILURES); then $(RUN) pytest tests $(PYTEST_RERUN_OPTIONS); fi
	@ rm -rf $(FAILURES)
	$(RUN) pytest tests $(PYTEST_OPTIONS)
	$(RUN) coveragespace $(REPOSITORY) overall

.PHONY: read-coverage
read-coverage:
	bin/open htmlcov/index.html

# DOCUMENTATION ###############################################################

DOCS_PATH := mkdocs/docs
SITE_PATH := mkdocs/site

mkdocs-uml: $(DOCS_PATH)/uml ## Generate UML Diagram
$(DOCS_PATH)/uml: $(MODULES)
	@ mkdir -p $(DOCS_PATH)/uml
	@ $(RUN) pyreverse $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	@ mv -f packages_$(PACKAGE).png $(DOCS_PATH)/uml/packages.png
	@ mv -f classes_$(PACKAGE).png $(DOCS_PATH)/uml/classes.png

mkdocs-api: $(DOCS_PATH)/api ## Generate API documentation
$(DOCS_PATH)/api: $(MODULES)
	@ mkdir -p $(DOCS_PATH)/api
	@ cd $(DOCS_PATH)/api; \
		PYTHONPATH=$(shell pwd); \
		$(RUN) pydocmd simple async_btree.definition+ > definition.md; \
		$(RUN) pydocmd simple async_btree.analyze async_btree.stringify_analyze async_btree.Node > analyze.md; \
		$(RUN) pydocmd simple async_btree.control+ > control.md; \
		$(RUN) pydocmd simple async_btree.decorator+ > decorator.md ; \
		$(RUN) pydocmd simple async_btree.leaf+ > leaf.md ;\
		$(RUN) pydocmd simple async_btree.parallele+ > parallele.md ; \
		$(RUN) pydocmd simple async_btree.utils+ > utils.md
# Add here all other package generation
# PYTHONPATH=$(shell pwd) is a workaround to https://github.com/NiklasRosenstein/pydoc-markdown/issues/30

MK_FILES = $(DOCS_PATH)/index.md $(DOCS_PATH)/license.md $(DOCS_PATH)/changelog.md $(DOCS_PATH)/code_of_conduct.md

mkdocs-md: $(MK_FILES) # Copy standard document
$(DOCS_PATH)/index.md: README.md
	@ cp -f README.md $(DOCS_PATH)/index.md
$(DOCS_PATH)/license.md: LICENSE.md
	@ cp -f LICENSE.md $(DOCS_PATH)/license.md
$(DOCS_PATH)/changelog.md: CHANGELOG.md
	@ cp -f CHANGELOG.md $(DOCS_PATH)/changelog.md
$(DOCS_PATH)/code_of_conduct.md: CODE_OF_CONDUCT.md
	@ cp -f CODE_OF_CONDUCT.md $(DOCS_PATH)/code_of_conduct.md

mkdocs-site: mkdocs/mkdocs.yml mkdocs-uml mkdocs-api mkdocs-md ## Build Documentation Site
	@ cd mkdocs; \
	  $(RUN) mkdocs build
	@ rm -rf docs/
	@ mv mkdocs/site docs/	

.clean-docs: ## remove all generated files
	@ rm -rf mkdocs/site
	@ rm -rf $(DOCS_PATH)/uml
	@ rm -rf $(DOCS_PATH)/api
	@ rm -rf $(DOCS_PATH)/index.md
	@ rm -rf $(DOCS_PATH)/license.md
	@ rm -rf $(DOCS_PATH)/changelog.md
	@ rm -rf $(DOCS_PATH)/code_of_conduct.md

docs: mkdocs-site ## Generate documentation and UML

# BUILD #######################################################################

DIST_FILES := dist/*.tar.gz dist/*.whl

.PHONY: dist
dist: install check test $(DIST_FILES)
$(DIST_FILES): $(MODULES) pyproject.toml
	rm -f $(DIST_FILES)
	poetry build

# RELEASE #####################################################################

.PHONY: upload
upload: dist ## Upload the current version to PyPI
	git diff --name-only --exit-code
	poetry publish
	bin/open https://pypi.org/project/$(PROJECT)

# CLEANUP #####################################################################

.PHONY: clean
clean: .clean-build .clean-test .clean-install .clean-docs ## Delete all generated and temporary files

.PHONY: .clean-install
.clean-install:
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov

.PHONY: .clean-build
.clean-build:
	rm -rf *.spec dist build

# HELP ########################################################################

.PHONY: help
help: all
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help


.PHONY: update-from-template

update-from-template:
	@git diff --name-only --exit-code
	cookiecutter gh:geronimo-iia/template-python --checkout feature/poetry-1.0.0  --config-file .cookiecutter.yaml --output-dir .. --no-input --overwrite-if-exists
	git status # shows lots of overridden files
	git add . -p # walk through patchsets, selecting files for adding
	git commit -m "Updated from template."
