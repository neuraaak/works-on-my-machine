# Getting Started with WOMM

This guide will help you install and start using WOMM (Works On My Machine) for managing your development environments.

## Installation

### Requirements

- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Internet connection** (for downloading dependencies)

### From PyPI (Recommended)

The easiest way to install WOMM is from PyPI:

```bash
pip install works-on-my-machine
```

Alternative short name:

```bash
pip install womm
```

### From Source

For the latest development version or to contribute:

```bash
# Clone the repository
git clone https://github.com/neuraaak/works-on-my-machine.git
cd works-on-my-machine

# Install using the installer script
python womm.py install
```

### Development Installation

For development with editable install:

```bash
# Clone and install in development mode
git clone https://github.com/neuraaak/works-on-my-machine.git
cd works-on-my-machine
pip install -e ".[dev]"
```

### Verify Installation

After installation, restart your terminal and verify:

```bash
womm --version
womm --help
```

## First Steps

### Create Your First Python Project

Create a fully configured Python project with one command:

```bash
womm new python my-awesome-app
```

This creates:

- Project directory structure
- Virtual environment (`.venv/`)
- Configuration files (`pyproject.toml`, `.pre-commit-config.yaml`)
- Development tools setup (Black, pytest, mypy, ruff)
- VSCode settings (`.vscode/settings.json`)
- Git repository initialization

### Create Your First JavaScript Project

Create a JavaScript/Node.js project:

```bash
womm new javascript my-react-app
```

For React projects:

```bash
womm new javascript my-react-app --type react
```

For Vue projects:

```bash
womm new javascript my-vue-app --type vue
```

### Interactive Mode

Let WOMM guide you through project creation:

```bash
womm new --interactive
```

WOMM will:

1. Ask for project type (Python/JavaScript)
2. Detect existing configurations
3. Prompt for project name and details
4. Setup appropriate tooling

## Setup Existing Projects

### Python Project Setup

Add professional tooling to an existing Python project:

```bash
cd existing-project
womm setup python
```

This adds:

- Virtual environment
- Black formatter configuration
- pytest testing framework
- mypy type checker
- ruff linter
- Pre-commit hooks
- VSCode integration

### JavaScript Project Setup

Setup JavaScript project with modern tooling:

```bash
cd existing-js-project
womm setup javascript
```

This adds:

- ESLint configuration
- Prettier formatter
- Jest testing framework
- Package.json scripts
- VSCode integration

### Auto-Detection

Let WOMM detect your project type:

```bash
cd existing-project
womm setup detect
```

WOMM analyzes:

- Existing files (`package.json`, `requirements.txt`)
- Project structure
- Configuration files
- Installed dependencies

## Complete Workflow Example

Here's a complete example of creating and working with a Python project:

```bash
# 1. Create new Python project
womm new python my-api

# 2. Navigate to project
cd my-api

# 3. Activate virtual environment
source .venv/bin/activate  # Unix
# or
.venv\Scripts\activate     # Windows

# 4. Install additional dependencies
pip install fastapi uvicorn

# 5. Run linting
womm lint

# 6. Check spelling
womm spell

# 7. Run tests
pytest

# 8. Format code
black .
```

## Configuration Options

### Command-Line Options

#### New Command

```bash
womm new <language> <name> [OPTIONS]

Options:
  --type TEXT          Project type (react, vue, etc.)
  --interactive        Interactive mode with prompts
  --template TEXT      Use specific template
  --help              Show help message
```

#### Setup Command

```bash
womm setup <language> [OPTIONS]

Options:
  --path TEXT         Project path (default: current directory)
  --interactive       Interactive mode
  --force            Force overwrite existing files
  --help             Show help message
```

### Interactive Configuration

Use interactive mode for guided setup:

```bash
# Interactive project creation
womm new --interactive

# Interactive setup
womm setup --interactive
```

WOMM will prompt you for:

- Language/framework choice
- Project name and details
- Tool preferences
- Configuration options

## Using Templates

### List Available Templates

```bash
womm templates list
```

### Create Template from Project

Save your project configuration as a reusable template:

```bash
cd my-configured-project
womm templates create my-template
```

### Use Template for New Project

Create a new project from a template:

```bash
womm templates use my-template new-project
```

Templates preserve:

- Configuration files
- Directory structure
- Tool settings
- Custom scripts

## Project Structure

### Python Project Structure

```text
my-python-project/
├── .venv/                    # Virtual environment
├── .vscode/                  # VSCode settings
│   └── settings.json
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── .gitignore
├── .pre-commit-config.yaml   # Pre-commit hooks
├── pyproject.toml            # Project configuration
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
└── README.md
```

### JavaScript Project Structure

```text
my-js-project/
├── node_modules/             # Dependencies
├── src/
│   └── index.js
├── tests/
├── .vscode/                  # VSCode settings
├── .eslintrc.js              # ESLint configuration
├── .prettierrc               # Prettier configuration
├── jest.config.js            # Jest configuration
├── package.json              # Project manifest
├── .gitignore
└── README.md
```

## Platform-Specific Features

### Windows Integration

On Windows, WOMM can integrate with the context menu:

```bash
# Install with context menu integration
womm install --context-menu

# This adds a "New WOMM Project" option to your right-click menu
```

### Cross-Platform Support

WOMM works seamlessly on:

- **Windows** (10/11)
- **macOS** (10.15+)
- **Linux** (Ubuntu, Debian, Fedora, Arch)

Platform-specific features are automatically detected and configured.

## Code Quality Tools

### Linting

Run linters on your project:

```bash
# Lint current directory
womm lint

# Lint specific path
womm lint src/

# Lint with fix
womm lint --fix
```

### Spell Checking

Check spelling in code and documentation:

```bash
# Check current directory
womm spell

# Check specific files
womm spell README.md docs/
```

## System Information

### View System Details

```bash
womm system info
```

Shows:

- Operating system
- Python version
- Installed tools
- PATH configuration

### Detect Installed Tools

```bash
womm system detect
```

Detects:

- Python interpreters
- Node.js/npm
- Development tools (Black, ESLint, etc.)
- Version control (Git)

## Troubleshooting

### Command Not Found

If `womm` command is not found after installation:

1. **Restart your terminal** - PATH updates require terminal restart
2. **Check installation**:

   ```bash
   pip show works-on-my-machine
   ```

3. **Verify PATH** - Ensure Python Scripts directory is in PATH
4. **Reinstall**:

   ```bash
   pip uninstall works-on-my-machine
   pip install works-on-my-machine
   ```

### Permission Errors

On Unix systems, you may need user installation:

```bash
pip install --user works-on-my-machine
```

Or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install works-on-my-machine
```

### Import Errors

If you get import errors:

1. **Check Python version**:

   ```bash
   python --version  # Should be 3.10+
   ```

2. **Reinstall dependencies**:

   ```bash
   pip install --upgrade --force-reinstall works-on-my-machine
   ```

### Windows PATH Issues

If commands don't work on Windows:

1. Run as Administrator:

   ```bash
   python womm.py install
   ```

2. Manually add to PATH (Settings → System → Environment Variables)
3. Restart terminal or reboot

## Next Steps

Now that you have WOMM installed and working:

1. **Explore Commands** - See [CLI Reference](cli/index.md) for all commands
2. **Learn Configuration** - Read [Configuration Guide](guides/configuration.md)
3. **View Examples** - Check [Examples](examples/index.md) for common use cases
4. **Understand Architecture** - Review [API Reference](api/index.md)
5. **Contribute** - See [Development Guide](guides/development.md)

## Getting Help

- **Documentation**: [https://neuraaak.github.io/works-on-my-machine/](https://neuraaak.github.io/works-on-my-machine/)
- **Issues**: [GitHub Issues](https://github.com/neuraaak/works-on-my-machine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neuraaak/works-on-my-machine/discussions)

---

Ready to eliminate "it works on my machine" problems? Start creating professional development environments with WOMM! 🚀
