# Change Log

## 1.2.1 (next)


## 1.2.0 (2023-05-11)

Features, from [#24](https://github.com/geronimo-iia/async-btree/issues/24) :

- Removing inner exception handling, in order to code like usual, catch what we want and manage exception as needed
- add function failure_on_exception : avoid raising and manage it in btree with a false meaning
- add function ignore_exception : ignore specific exception

Fix:
- mypy cast issue on decorated function.
- name attribute on operator
- add test about metadata node name and properties
- function name access compliant with mypi

Technical Update:

- use local .venv directory for virtual env -> better integration with visual studio
- update development dependencies
- use ruff as replacement of flake8, flakehell,...
- use mkdocs as replacement of sphinx
- simplify Makefile
- change 'master' branch for 'main'

## 1.1.1 (2020-11-21)

- simplify `analyze` function
- fix parallele implementation

## 1.1.0 (2020-11-20)

- remove falsy evaluation of exception
- add ignore_exception decorator
- use sync or async function in parameters operator
- decision control return Success per default rather than act as a failure if no failure tree dependency is set.
- add test on python 3.8

## 1.0.2 (2020-11-15)

- update curio version > 1
- add pytest-curio and rewrote test unit

## 1.0.1 (2020-01-31)

- update from template-python
- use poetry 1.0.x

## 1.0.0 (2019-09-01)

- rework documentation build process (see mkdocs folder)
- configure github page under master/docs
- configure documentation site on pypi
- add doc style on all function 
- standardize parameter name
- fix dev documentation dependency

## 0.1.2 (2019-07-05)

- Stable version flag
- Remove alpha note

## 0.1.1 (2019-07-05)

Removed version due to configuration error.

## 0.1.0 (2019-07-05)

- Added Project Management: 
- initial project structure based on [jacebrowning/template-python](https://github.com/jacebrowning/template-python)
  - initial project configuration
  - follow [Semantic Versioning](https://semver.org/)
  - configure [travis-ci](https://travis-ci.org)
  - publish alpha version (not functional) on [pypi](https://pypi.org)
  - configure [coverage](https://coveralls.io)
  - configure [scrutinizer](https://scrutinizer-ci.com/)
  - remove pylint.ini to a simple .pylintrc (add ide support)
  - disable pylint bad-continuation (bug with pep8 formater)
  - declare extra dependency
  - configure black and isort
  - refactorise makefile poetry run
  - introduce flake8 as linter
- Documentation:
  - replace mkdocs with [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown)
- Code:
  - define 'definition' module to declare all common definiton of btree
  - define 'utils' module to declare few async function like afilter, amap
  - fix flake8 syntax error
  - fix mypy typing error
  - add basic test unit
  - fix typing declaration
  - complete code coverage

