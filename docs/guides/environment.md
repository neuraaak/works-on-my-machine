# Environment Setup Guide

Setting up your development environment for Python and JavaScript projects with WOMM.

## Python Environment

### Virtual Environments

WOMM automatically creates virtual environments for Python projects:

```bash
# Create project (includes .venv/)
womm new python my-project
cd my-project

# Activate environment
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows

# Deactivate
deactivate
```

### Python Version Management

**Using pyenv** (Unix/macOS):

```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python version
pyenv install 3.11.0
pyenv global 3.11.0

# Verify
python --version
```

**Using py launcher** (Windows):

```bash
# List installed versions
py --list

# Use specific version
py -3.11 -m venv .venv
```

### Development Tools

WOMM configures these tools automatically:

- **Black** - Code formatter
- **pytest** - Testing framework
- **mypy** - Type checker
- **ruff** - Linter

## JavaScript Environment

### Node.js and npm

**Installation:**

- Download from [nodejs.org](https://nodejs.org/)
- Or use version manager (nvm, fnm)

**Using nvm** (Unix/macOS):

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install Node.js
nvm install 18
nvm use 18
```

**Using nvm-windows** (Windows):

```powershell
# Download from https://github.com/coreybutler/nvm-windows
nvm install 18
nvm use 18
```

### JavaScript Development Tools

WOMM configures:

- **ESLint** - Linter
- **Prettier** - Code formatter
- **Jest** - Testing framework

## IDE Integration

### VSCode

WOMM creates `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

**Recommended Extensions:**

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)

## Pre-commit Hooks

WOMM sets up pre-commit hooks for Python projects:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
```

**Install hooks:**

```bash
pip install pre-commit
pre-commit install
```

## Git Configuration

### Global Settings

```bash
# Set user info
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Set editor
git config --global core.editor "code --wait"

# Enable color
git config --global color.ui auto
```

### Project-Level

WOMM creates `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# JavaScript
node_modules/
dist/
build/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

## Platform-Specific Setup

### Windows

**Install Requirements:**

```powershell
# Install Python
# Download from python.org

# Install Git
# Download from git-scm.com

# Install Node.js
# Download from nodejs.org

# Verify installations
python --version
git --version
node --version
```

**PATH Configuration:**

```powershell
# Add Python Scripts to PATH
$env:PATH += ";C:\Users\YourUser\AppData\Local\Programs\Python\Python311\Scripts"

# Make permanent via System Properties → Environment Variables
```

### macOS

**Using Homebrew:**

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install python@3.11
brew install node
brew install git

# Verify
python3 --version
node --version
git --version
```

### Linux

**Ubuntu/Debian:**

```bash
# Update packages
sudo apt update

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Git
sudo apt install git
```

## Troubleshooting

### Python Not Found

```bash
# Windows - Use py launcher
py -3.11 --version

# Unix - Check PATH
which python3
echo $PATH
```

### Virtual Environment Issues

```bash
# Recreate environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### npm Permission Errors

```bash
# Use nvm (recommended)
# Or configure npm prefix
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

## See Also

- [Getting Started](../getting-started.md)
- [Prerequisites Guide](prerequisites.md)
- [Configuration Guide](configuration.md)
- [Development Guide](development.md)
