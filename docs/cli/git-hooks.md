# Git Hooks

This project uses [pre-commit](https://pre-commit.com/) to run consistent
quality checks before each commit. The hooks are declared in
`.pre-commit-config.yaml`; the legacy `.hooks` mechanism is no longer used.

## Setup

Prepare the uv environment and install the hook once per clone:

```bash
git config --unset core.hooksPath
uv sync --extra dev --extra test
uv run --no-sync pre-commit install
```

The first command removes a legacy custom hooks path when one was configured.
It can report that the key does not exist on a fresh clone; no action is needed
in that case.

## Checks

Commits run the following checks:

1. file hygiene and configuration validation;
2. Ruff formatting and linting;
3. Ty type checking;
4. import-linter architecture contracts;
5. `_version.py` synchronization when `pyproject.toml` changes.

Hooks that modify files stop the commit so the changes can be reviewed and
staged explicitly.

## Manual execution

Run the complete hook suite through the project task:

```bash
uv run --no-sync poe pre-commit
```

Run a specific hook directly when diagnosing a failure:

```bash
uv run --no-sync pre-commit run ruff --all-files
uv run --no-sync pre-commit run ty --all-files
```

The same quality commands are available individually with `poe lint`,
`poe types`, `poe imports`, and `poe test`. Run `poe` without a task to list
all available development commands.
