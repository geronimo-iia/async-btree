# Project settings
PROJECT := async-btree
PACKAGE := async_btree
REPOSITORY := geronimo-iia/async-btree
DOC_PATHS = ./docs

# Project paths
PACKAGES := $(PACKAGE) tests
CONFIG := $(wildcard *.py)
MODULES := $(wildcard $(PACKAGE)/*.py)

# Virtual environment paths
VIRTUAL_ENV ?= .venv
RUN := poetry run

# MAIN TASKS ##################################################################

SNIFFER := $(RUN) sniffer

.PHONY: all
all: install

.PHONY: ci
ci: format check test mkdocs ## Run all tasks that determine CI status

.PHONY: watch
watch: install .clean-test ## Continuously run all CI tasks when files chanage
	$(SNIFFER)

.PHONY: run ## Start the program
run: install
	$(RUN) python $(PACKAGE)/__main__.py

# SYSTEM DEPENDENCIES #########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

# PROJECT DEPENDENCIES ########################################################

DEPENDENCIES := $(VIRTUAL_ENV)/.poetry-$(shell bin/checksum pyproject.toml poetry.lock)

.PHONY: install
install: .venv $(DEPENDENCIES) .cache 

$(DEPENDENCIES): poetry.lock
	@ poetry config settings.virtualenvs.in-project false
	poetry install -E curio
	@ touch $@

poetry.lock: pyproject.toml
	poetry lock
	@ touch $@

.cache:
	@ mkdir -p .cache

.venv:
	@ mkdir -p $(VIRTUAL_ENV)

# CHECKS ######################################################################

ISORT := $(RUN) isort
PYLINT := $(RUN) pylint
FLAKE := $(RUN) flake8
BLACK := $(RUN) black
MYPI := $(RUN) mypy
PYCODESTYLE := $(RUN) pycodestyle
PYDOCSTYLE := $(RUN) pydocstyle


.PHONY: check
check: isort black flake mypy pydocstyle ## Run linters and static analysis

.PHONY: isort
isort: install
	$(ISORT) $(PACKAGES) --recursive --apply

.PHONY: black
black: install
	$(BLACK) $(PACKAGES) 

.PHONY: pylint
pylint: install
	$(PYLINT) $(PACKAGE)

.PHONY: mypy
mypy: install
	$(MYPI) $(PACKAGE)  --config-file=.mypy.ini

.PHONY: pydocstyle
pydocstyle: install
	$(PYDOCSTYLE) $(PACKAGES) $(CONFIG)

.PHONY: flake
flake: install ## Run flake8 linters
	$(FLAKE) $(PACKAGES)


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

.PHONY: docs
docs: .clean-docs uml mkdocs ## Generate documentation and UML

.PHONY: mkdocs
mkdocs: install
	@cd docs-source && $(RUN) pydocmd build
	@mv docs-source/_build/site/* ./docs

.PHONY: uml
uml: install docs/*.png

docs/*.png: $(MODULES)
	@mkdir -p $(DOC_PATHS)/uml
	@$(RUN) pyreverse $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png docs/uml/classes.png
	- mv -f packages_$(PACKAGE).png docs/uml/packages.png

.PHONY: mkdocs-live
mkdocs-live: mkdocs
	eval "sleep 3; bin/open http://127.0.0.1:8000" &
	$(RUN) pydocmd serve

# BUILD #######################################################################

DIST_FILES := dist/*.tar.gz dist/*.whl
EXE_FILES := dist/$(PROJECT).*

.PHONY: dist
dist: install $(DIST_FILES)
$(DIST_FILES): $(MODULES) pyproject.toml
	rm -f $(DIST_FILES)
	poetry build

.PHONY: exe
exe: install $(EXE_FILES)
$(EXE_FILES): $(MODULES) $(PROJECT).spec
	# For framework/shared support: https://github.com/yyuu/pyenv/wiki
	$(RUN) pyinstaller $(PROJECT).spec --noconfirm --clean

$(PROJECT).spec:
	$(RUN) pyi-makespec $(PACKAGE)/__main__.py --onefile --windowed --name=$(PROJECT)

# RELEASE #####################################################################

.PHONY: upload
upload: dist ## Upload the current version to PyPI
	git diff --name-only --exit-code
	poetry publish
	bin/open https://pypi.org/project/$(PROJECT)

# CLEANUP #####################################################################

.PHONY: clean
clean: .clean-build .clean-docs .clean-test .clean-install ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean
	rm -rf $(VIRTUAL_ENV)

.PHONY: .clean-install
.clean-install:
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov

.PHONY: .clean-docs
.clean-docs:
	rm -rf docs/* docs-source/_build


.PHONY: .clean-build
.clean-build:
	rm -rf *.spec dist build

# HELP ########################################################################

.PHONY: help
help: all
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
