# Contributing

This project is based on [Jace's Python Template](https://github.com/jacebrowning/template-python) and heevly customized...
This is a cookiecutter template for a typical Python library following modern packaging conventions. It utilizes popular libraries alongside Make and Graphviz to fully automate all development and deployment tasks.

My main requirement was to find something wich use Poetry project to manage python dependencies.
Other template exist like [Cookiecutter PyPackage](https://github.com/audreyr/cookiecutter-pypackage), maybe a next time ?


## Setup

### Requirements

* Make:
    * macOS: `$ xcode-select --install`
    * Linux: [https://www.gnu.org/software/make](https://www.gnu.org/software/make)
    * Windows: [https://mingw.org/download/installer](https://mingw.org/download/installer)
* Pyenv: [https://github.com/pyenv/pyenv#installation](https://github.com/pyenv/pyenv#installation)
* Python: `$ pyenv install 3.7.3`

  Note for [MacOS 10.14 user](https://github.com/pyenv/pyenv/issues/544):
  ```bash
    SDKROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.14.sdk MACOSX_DEPLOYMENT_TARGET=10.14 pyenv install 3.7.3
  ```
* Poetry: [https://poetry.eustace.io/docs/#installation](https://poetry.eustace.io/docs/#installation)

  Note:
  ```bash
  poetry config settings.virtualenvs.path "${HOME}/.virtualenvs"
  ```
* Graphviz:
    * macOS: `$ brew install graphviz`
    * Linux: [https://graphviz.org/download](https://graphviz.org/download/)
    * Windows: [https://graphviz.org/download](https://graphviz.org/download/)

To confirm these system dependencies are configured correctly:

```text
$ make doctor
```

### Installation

Install project dependencies into a virtual environment:

```text
$ make install
```

## Development Tasks

### Manual

Run the tests:

```text
$ make test
```

Run static analysis:

```text
$ make check
```

Build the documentation:

```text
$ make docs
```

### Automatic

Keep all of the above tasks running on change:

```text
$ make watch
```

> In order to have OS X notifications, `brew install terminal-notifier`.

## Continuous Integration

The CI server will report overall build status:

```text
$ make ci
```

## Release Tasks

Release to PyPI:

```text
$ make upload
```
