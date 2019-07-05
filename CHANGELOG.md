
# 0.1.2 (2019-07-05)

- Stable version flag
- Remove alpha note

# 0.1.0 (2019-07-05)

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

