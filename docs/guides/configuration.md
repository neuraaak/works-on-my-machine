# Configuration Guide

Learn how to configure WOMM for your development workflow.

## Command-Line Options

### Create Command

```bash
womm create <template> <destination> [OPTIONS]
```

**Options:**

- `--data KEY=VALUE` - Pre-fill a template answer (repeatable)
- `--defaults` - Use template defaults instead of prompting
- `--force` - Render into a non-empty destination
- `--pretend` - Simulate the rendering without writing anything
- `--setup` - Prepare the environment after rendering
- `--help` - Show help message

**Examples:**

```bash
# React-flavored JavaScript project
womm create official/javascript my-app --data framework=react

# Non-interactive, using template defaults
womm create official/python my-api --defaults --data project_name=my-api
```

### Setup Command

```bash
womm setup <language> [OPTIONS]
```

**Options:**

- `--path TEXT` - Project path (default: current directory)
- `--interactive` - Interactive mode
- `--force` - Force overwrite
- `--help` - Show help

**Examples:**

```bash
# Setup Python project
womm setup python

# Auto-detect
womm setup detect

# Interactive
womm setup --interactive
```

### Lint Command

```bash
womm lint [path] [OPTIONS]
```

**Options:**

- `--fix` - Auto-fix issues
- `--verbose` - Verbose output
- `--help` - Show help

### Template Command

```bash
womm template <action> [OPTIONS]
```

**Actions:**

- `list` - List catalog templates
- `show <identifier>` - Show a single catalog entry
- `add <identifier> <source>` - Register a local Copier template
- `remove <identifier>` - Unregister a user template
- `update <identifier> <source>` - Point a user template at a new source
- `init <destination>` - Scaffold a new Copier template skeleton

## Template Configuration

Templates are standard [Copier](https://copier.readthedocs.io/) templates: a
`copier.yml` declaring the questions plus a `template/` directory of
Jinja-rendered files. User-registered templates are recorded under
`~/.womm/templates/` (or `%WOMM_HOME%` if set). See
[Template Management](../cli/templates.md) for the full CLI reference.

### Registering a Template

```bash
womm template add my-template ./path/to/my-copier-template
```

### Listing and Rendering

```bash
# List templates
womm template list

# Render a project from a template (rendering is `womm create`, not `womm template`)
womm create my-template ./new-project
```

## Platform-Specific Configuration

### Windows

```bash
# Install with context menu
womm install --context-menu

# Adds right-click "New WOMM Project" option
```

### macOS/Linux

```bash
# Standard installation
pip install works-on-my-machine

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

## Environment Variables

WOMM respects these environment variables:

- `WOMM_HOME` - WOMM configuration directory (default: `~/.womm`)
- `WOMM_TEMPLATES_DIR` - Templates directory
- `PYTHON_VERSION` - Default Python version for projects
- `NODE_VERSION` - Default Node.js version

**Example:**

```bash
export WOMM_HOME="$HOME/.config/womm"
export WOMM_TEMPLATES_DIR="$HOME/my-templates"
```

## Project Configuration

### Python Projects

**pyproject.toml** - Main configuration file:

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.10"

[tool.black]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
```

### JavaScript Projects

**package.json** - Main configuration:

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint src/",
    "test": "jest"
  }
}
```

**.eslintrc.js** - Linter configuration:

```javascript
module.exports = {
  extends: ["eslint:recommended"],
  env: {
    node: true,
    es2021: true,
  },
};
```

## Best Practices

1. **Version Control** - Always commit configuration files
2. **Templates** - Create templates for recurring project types
3. **Documentation** - Document custom configurations in README
4. **Consistency** - Use same configuration across team
5. **Testing** - Test configurations before applying to production

## See Also

- [Getting Started](../getting-started.md)
- [CLI Reference](../cli/index.md)
- [Examples](../examples/index.md)
- [Development Guide](development.md)
