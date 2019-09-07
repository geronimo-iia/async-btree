# Contributing

This project is based on [Jace's Python Template](https://github.com/jacebrowning/template-python) and heevly customized...
This is a cookiecutter template for a typical Python library following modern packaging conventions. It utilizes popular libraries alongside Make and Graphviz to fully automate all development and deployment tasks.

My main requirement was to find something wich use Poetry project to manage python dependencies.
Other template exist like [Cookiecutter PyPackage](https://github.com/audreyr/cookiecutter-pypackage), maybe a next time ?

After this first experience, i wrote a fork of [Jace's Python Template](https://github.com/jacebrowning/template-python) that you
could retrieve on [Geronimo-iaa's Python Template](https://github.com/geronimo-iia/template-python)

## Setup

### Requirements

* Make:
    * macOS: `$ xcode-select --install`
    * Linux: [https://www.gnu.org/software/make](https://www.gnu.org/software/make)
    * Windows: [https://mingw.org/download/installer](https://mingw.org/download/installer)

* Pyenv: [https://github.com/pyenv/pyenv#installation](https://github.com/pyenv/pyenv#installation)
  
  Pyenv will manage all our python version.

* Python: `$ pyenv install 3.7.3`

  Note for [MacOS 10.14 user](https://github.com/pyenv/pyenv/issues/544):
  ```bash
    SDKROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.14.sdk MACOSX_DEPLOYMENT_TARGET=10.14 pyenv install 3.7.3
  ```

* Poetry: [https://poetry.eustace.io/docs/#installation](https://poetry.eustace.io/docs/#installation)
  
  Poetry will manage our dependencies and create our virtual environment for us.

* Graphviz:
    * macOS: `$ brew install graphviz`
    * Linux: [https://graphviz.org/download](https://graphviz.org/download/)
    * Windows: [https://graphviz.org/download](https://graphviz.org/download/)

To confirm these system dependencies are configured correctly:

```bash
$ make doctor
```

### Installation

Install project dependencies into a virtual environment:

```bash
$ make install
```

Note:
- this target create a dummy file ```.install```. The makefile rule depends on pyproject.toml and
poetry.lock file
- if for whatever reason, you have to force installation, just remove this ```.install``` file and 
execute a ```make install```


## Development Tasks

### Manual

Run the tests:

```bash
$ make test
```

Run static analysis:

```bash
$ make check
```

Build the documentation:

```bash
$ make docs
```

### Automatic

Keep all of the above tasks running on change:

```text
$ make watch
```

> In order to have OS X notifications, `brew install terminal-notifier`.

### Integration With Visual Studio Code

Even if we use fabulous tool like pyenv, poetry, ... at the end, we just want to go on, and code.

So here, few detail of my installation.

- .bashrc
    ```bash
    # init pyenv with default python version
    if command -v pyenv 1>/dev/null 2>&1; then
    eval "$(pyenv init -)"
    fi

    # add poetry in path
    export PATH="$HOME/.poetry/bin:$PATH"

    # Add Visual Studio Code (code)
    export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
    ```

- poetry configuration: all is let with default
    ```text
    settings.virtualenvs.create = true
    settings.virtualenvs.in-project = false
    settings.virtualenvs.path = "/Users/xxxx/Library/Caches/pypoetry/virtualenvs"
    repositories = {}
    ```
    As now, i cannot have a working system with 'settings.virtualenvs.in-project' set to true
    or 'settings.virtualenvs.path' setted with a custom path.

- How Launch Visual Studio Code within virtual environment created by poetry ?
    After do a ```make install```, you have to do:
    ```bash
    poetry shell
    code .
    ```
    ```poetry shell``` will activate project virtual environment.

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
