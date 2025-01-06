# Contributing

This project is based on [Geronimo-iaa's Python Template](https://github.com/geronimo-iia/python-module-template).
This is a cookiecutter template for a typical Python library following modern packaging conventions. 
It utilizes popular libraries to fully automate all development and deployment tasks.


## Setup

### Requirements

You will need:

* Python 3.9"+
* [Pyenv](https://github.com/pyenv/pyenv#installation)
* [poetry](https://python-poetry.org/)
* Make


### Make Installation

A powerfull tool:
* macOS: `$ xcode-select --install`
* Linux: [https://www.gnu.org/software/make](https://www.gnu.org/software/make)
* Windows: [https://mingw.org/download/installer](https://mingw.org/download/installer)

### Pyenv Installation

Pyenv will manage all our python version.
Follow [https://github.com/pyenv/pyenv#installation](https://github.com/pyenv/pyenv#installation)


### Python Installation

 Do:

 `$ pyenv install 3.8`


### Poetry Installation: [https://poetry.eustace.io/docs/#installation](https://poetry.eustace.io/docs/#installation)

Poetry will manage our dependencies and create our virtual environment for us.

## Make Target list


| Name                    | Comment                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| make install            | Install project dependencies                                                                    |
| make configure          | Configure poetry                                                                                |
| make tag                | Create and push a tag based on current project version. This will launch github release action. |
| make next-patch-version | Increment patch version of the project.                                                         |
|                         |


## Poe Target list


| Name                    | Comment                                  |
| ----------------------- | ---------------------------------------- |
| poetry poe types        | Run the type checker                     |
| poetry poe lint         | Run linting tools on the code base       |
| poetry poe style        | Validate black code style                |
| poetry poe test         | Run unit tests                           |
| poetry poe check        | Run all checks on the code base          |
| poetry poe build        | Builds module                            |
| poetry poe publish      | Publishes the package                    |
| poetry poe docs         | Builds  site documentation.              |
| poetry poe docs-publish | Build and publish site documentation.    |
| poetry poe clean        | Delete all generated and temporary files |
| poetry poe requirements | Generate requirements.txt                |
|                         |


You could retrieve those commands with `poetry poe`. It will output something like this :

```
Usage:
  poetry poe [global options] task [task arguments]

Global options:
  -h, --help            Show this help page and exit
  --version             Print the version and exit
  -v, --verbose         Increase command output (repeatable)
  -q, --quiet           Decrease command output (repeatable)
  -d, --dry-run         Print the task contents but don't actually run it
  -C PATH, --directory PATH
                        Specify where to find the pyproject.toml
  -e EXECUTOR, --executor EXECUTOR
                        Override the default task executor
  --ansi                Force enable ANSI output
  --no-ansi             Force disable ANSI output

Configured tasks:
  types                 Run the type checker
  lint                  Run linting tools on the code base
  style                 Validate black code style
  test                  Run unit tests
  check                 Run all checks on the code base
  build                 Build module
  publish               Publish module
  docs                  Build site documentation
  docs-publish          Publish site documentation
  clean                 Remove all generated and temporary files
  requirements          Generate requirements.txt

```
