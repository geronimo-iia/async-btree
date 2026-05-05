# Contributing

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Make

## Repository Layout

```
async-btree/
├── async_btree/          # library source
│   ├── definition.py     # core types: SUCCESS, FAILURE, NodeMetadata, ControlFlowException
│   ├── leaf.py           # leaf nodes: action(), condition()
│   ├── control.py        # control flow: sequence(), selector(), fallback(), decision(), repeat_until()
│   ├── decorator.py      # decorators: retry(), inverter(), alias(), ignore_exception(), ...
│   ├── parallele.py      # concurrent execution: parallele()
│   ├── runner.py         # BTreeRunner context manager
│   ├── analyze.py        # tree introspection: analyze(), stringify_analyze()
│   ├── utils.py          # helpers: to_async(), amap(), afilter(), run()
│   └── __init__.py       # public API exports
├── tests/                # test suite (asyncio, trio, asyncio+uvloop backends)
├── examples/             # usage examples (tutorials 1-4)
├── docs/                 # documentation source (MkDocs)
│   ├── gen_ref_pages.py  # auto-generates API reference pages
│   ├── migration/        # migration guides for major versions
│   └── brainstorming/    # internal design notes (gitignored)
├── .github/
│   └── workflows/
│       ├── package.yml   # CI: lint + test on push/PR to main
│       ├── release.yml   # CD: publish to PyPI + docs on git tag v*
│       └── doc.yml       # docs deploy on push to main
├── mkdocs.yml            # documentation configuration
├── pyproject.toml        # project metadata and dependencies
├── Makefile              # development tasks
└── uv.lock               # locked dependencies
```

## Setup

```bash
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# install dependencies
make install
```

## Make Targets

Run `make` to list all available targets.

| Target | Description |
| --- | --- |
| `make install` | Install dependencies |
| `make lock` | Lock dependencies |
| `make lint` | Check format, linting and types |
| `make lint-fix` | Fix all auto-fixable issues |
| `make test` | Run unit tests |
| `make check` | Run all checks (lint + test) |
| `make build` | Build module (runs check first) |
| `make publish` | Publish module (runs build first) |
| `make docs` | Build site documentation |
| `make docs-serve` | Serve documentation locally with live reload |
| `make docs-publish` | Publish site documentation to gh-pages |
| `make clean` | Remove all generated and temporary files |
| `make requirements` | Generate requirements.txt |

## Testing

Tests run against three backends — asyncio, trio, and asyncio+uvloop — parametrized automatically:

```bash
make install && make test
```

All test functions marked `@pytest.mark.anyio` run under all three backends via the `anyio_backend` fixture.

## Documentation

Sources live in `docs/`. API reference is auto-generated from docstrings — no manual edits needed in `docs/reference/`.

```bash
make docs-serve   # live preview at http://127.0.0.1:8000
make docs         # full build into site/
make docs-publish # deploy to gh-pages (CI does this on push to main)
```

## Release Process

1. Create a release branch from `main`:
   ```bash
   git checkout -b release/vX.Y.Z
   ```
2. Update `CHANGELOG.md`: replace `(unreleased)` with the release date `(YYYY-MM-DD)`
3. Bump version in `pyproject.toml`
4. Run all checks locally — all must pass before merging:
   ```bash
   make check    # lint + type check + tests (all backends)
   make docs     # documentation builds clean
   ```
5. Commit: `chore(release): bump version to X.Y.Z`
6. Open PR `release/vX.Y.Z` → `main`, verify CI passes (`package.yml` runs on all Python versions)
7. Merge PR into `main`
8. Tag and push from `main`:
   ```bash
   git tag vX.Y.Z
   git push origin main --tags
   ```
9. CI (`release.yml`) triggers on `v*` tag — builds, publishes to PyPI, creates GitHub release, deploys docs automatically

## Code Quality

```bash
make lint      # check format, linting, types
make lint-fix  # auto-fix format and linting issues
```

Tools: [ruff](https://docs.astral.sh/ruff/) for formatting/linting, [pyright](https://github.com/microsoft/pyright) for type checking.
