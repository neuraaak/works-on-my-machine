# Project Creation

Complete guide to creating new projects with WOMM. `womm create` renders a
project from a Copier template — the official catalog currently ships
`official/python` (optional Django) and `official/javascript` (optional
React or Vue, optional TypeScript).

## Overview

Project creation is delegated entirely to [Copier](https://copier.readthedocs.io/).
Every language, framework, and variant choice lives inside the template's
`copier.yml` — the CLI itself has no knowledge of "Python" or "JavaScript",
it only knows how to render a template identifier into a destination
directory. See [Template Management](templates.md) for how the catalog of
available templates is managed.

## Syntax

```bash
womm create <template> <destination> [OPTIONS]
```

- `TEMPLATE` - Catalog identifier, e.g. `official/python` or `official/javascript`
- `DESTINATION` - Directory to render the project into

## Options

| Option | Description |
| --- | --- |
| `--data KEY=VALUE` | Pre-fill a template answer. Repeatable. |
| `--defaults` | Use template defaults instead of prompting. |
| `--force` | Render into a non-empty destination. |
| `--pretend` | Simulate the rendering without writing anything. |
| `--setup` | Prepare the environment after rendering (virtualenv, dependencies, git). |
| `-v`, `--verbose` | Show detailed output. |

## Quick Start

```bash
# See what templates are available
womm template list

# Create a Python project, answering prompts interactively
womm create official/python ./my-python-app

# Create a JavaScript project non-interactively, with defaults
womm create official/javascript ./my-js-app --defaults --data project_name=my-js-app

# Pre-fill specific answers and prompt for the rest
womm create official/python ./my-api --data project_name=my-api --data framework=django

# Preview what would be rendered, without writing files
womm create official/python ./my-app --pretend

# Render and immediately prepare the dev environment
womm create official/python ./my-app --defaults --data project_name=my-app --setup
```

## How Answers Work

`--data KEY=VALUE` pre-fills a single Copier question; repeat the option for
each answer you want to supply. Any question not covered by `--data` is
either prompted for interactively, or filled from the template's declared
default when `--defaults` is passed. Values are passed through as raw
strings — Copier casts them according to the question's declared type in
`copier.yml`.

## Troubleshooting

### Destination Already Exists

```bash
# Re-render into a non-empty directory
womm create official/python ./existing-dir --force
```

### Unknown Template

```bash
# List the templates actually registered in the catalog
womm template list

# Inspect a single entry (source, version, description)
womm template show official/python
```

### Debug Mode

```bash
womm create official/python ./my-app -v
```

## See Also

- [Template Management](templates.md) - Manage the Copier template catalog (`list`, `show`, `add`, `remove`, `update`, `init`)
- [Getting Started](../getting-started.md) - Installation and first steps
- [CLI Reference](index.md) - Complete command documentation

---

This project creation guide reflects the Copier-based `womm create` command.
