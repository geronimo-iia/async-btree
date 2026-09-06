# async-btree

Async behavior tree library. Python 3.11+, anyio backend.

## Commands

```bash
make test        # run test suite
make lint        # check style
make lint-fix    # auto-fix style
make check       # lint + test
```

Run tests locally against Python 3.13:
```bash
uv run --python 3.13 pytest
```

## Key docs

- `docs/invariants.md` — invariants that must hold; breaking any is a bug
- `docs/decisions/` — ADRs explaining design choices
- `docs/concepts.md` — core concepts

## Conventions

- Conventional commits: `type(scope): short description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `chore`
- No body, no bullet list in commit messages
