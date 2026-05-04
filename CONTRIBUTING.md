# Contributing

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Make

## Setup

```bash
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# install dependencies (asyncio only)
make install

# install dependencies with curio support
make install-curio
```

## Make Targets

Run `make` to list all available targets.

| Target | Description |
| --- | --- |
| `make install` | Install dependencies (asyncio only) |
| `make install-curio` | Install dependencies with curio |
| `make lock` | Lock dependencies |
| `make lint` | Check format, linting and types |
| `make lint-fix` | Fix all auto-fixable issues |
| `make test` | Run unit tests |
| `make check` | Run all checks (lint + test) |
| `make build` | Build module (runs check first) |
| `make publish` | Publish module (runs build first) |
| `make docs` | Build site documentation |
| `make docs-publish` | Publish site documentation |
| `make clean` | Remove all generated and temporary files |
| `make requirements` | Generate requirements.txt |

## Testing

Tests run against two backends. By default `make install` installs asyncio only:

```bash
# asyncio backend
make install && make test

# curio backend
make install-curio && make test
```

Tests marked `@pytest.mark.curio` run under curio only.
Tests marked `@pytest.mark.asyncio` run under asyncio only.

## Code Quality

```bash
make lint      # check format, linting, types
make lint-fix  # auto-fix format and linting issues
```

Tools: [ruff](https://docs.astral.sh/ruff/) for formatting/linting, [pyright](https://github.com/microsoft/pyright) for type checking.
