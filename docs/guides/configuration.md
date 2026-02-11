# Configuration Guide

Learn how to configure WOMM for your development workflow.

## Command-Line Options

### New Command

```bash
womm new <language> <name> [OPTIONS]
```

**Options:**

- `--type TEXT` - Project type (react, vue, django, flask)
- `--interactive` - Interactive mode with prompts
- `--template TEXT` - Use specific template
- `--force` - Overwrite existing files
- `--help` - Show help message

**Examples:**

```bash
# React project
womm new javascript my-app --type react

# Interactive mode
womm new --interactive

# Use template
womm new python my-api --template fastapi-template
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

### Templates Command

```bash
womm templates <action> [OPTIONS]
```

**Actions:**

- `list` - List available templates
- `create <name>` - Create template from project
- `use <name> <output>` - Use template
- `delete <name>` - Delete template

## Template Configuration

Templates are stored in `~/.womm/templates/` and include:

### Template Metadata

`.womm-template.json`:

```json
{
  "name": "my-template",
  "description": "My custom template",
  "language": "python",
  "version": "1.0.0",
  "author": "Your Name",
  "variables": {
    "PROJECT_NAME": "{{project_name}}",
    "VERSION": "{{version}}"
  }
}
```

### Creating Templates

```bash
# Create from current project
cd my-configured-project
womm templates create my-template

# Template is saved to ~/.womm/templates/my-template/
```

### Using Templates

```bash
# List templates
womm templates list

# Use template
womm templates use my-template new-project
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
