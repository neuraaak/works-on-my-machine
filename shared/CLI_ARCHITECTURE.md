# 🔧 CLI Architecture - Works On My Machine

## Overview

The Works On My Machine project uses a **dual CLI architecture**:
1. **User-facing CLI** with Click (`womm.py`) - Modern, user-friendly command interface
2. **System command manager** (`shared/cli_manager.py`) - Centralized subprocess execution

This architecture provides both excellent UX and robust system command handling.

## File Structure

```
works-on-my-machine/
├── womm.py                  # Main CLI entry point (Click)
├── init.py                  # Installation wrapper (delegates to womm:install)
├── shared/
│   ├── cli_manager.py       # System command execution
│   ├── system_detector.py   # System detection (migrated)
│   └── ...
└── languages/
    ├── python/scripts/      # Python tools
    └── javascript/scripts/  # JavaScript tools
```

## Main Components

### 1. Click CLI (`womm.py`)

**Purpose**: Modern, user-friendly command interface with automatic help generation.

**Features**:
- Command grouping (`install`, `uninstall`, `new`, `lint`, `spell`, `system`, `deploy`, `context`)
- Automatic argument parsing and validation
- Built-in help system
- Cross-platform compatibility

**Example Usage**:
```bash
womm install                        # Install WOMM
womm uninstall                      # Remove WOMM
womm new python my-project          # Create Python project
womm new javascript --type=react    # Create React project
womm lint python --fix             # Lint and fix Python code
womm spell check ./src              # Spell check files
womm system install python node    # Install prerequisites
```

### 2. CLI Manager (`shared/cli_manager.py`)

**Purpose**: Centralized system command execution with consistent error handling.

**Features**:
- Standardized command execution
- Automatic logging and error handling
- Cross-platform command adaptation
- Multiple execution modes (silent, interactive, verbose)

**Example Usage**:
```python
from shared.cli_manager import run_command, run_silent

# Execute with logging
result = run_command(["npm", "install"], "Installing dependencies")

# Silent execution
result = run_silent(["git", "status"])
```

## Command Groups Structure

### Main Entry Point
```python
@click.group()
@click.version_option(version="1.0.0")
def womm():
    """🛠️ Works On My Machine - Universal development tools."""
    pass
```

### Command Groups
```python
@womm.group()
def new():
    """🆕 Create new projects."""
    pass

@womm.group()
def lint():
    """🎨 Code quality and linting tools."""
    pass

@womm.group()
def spell():
    """📝 Spell checking with CSpell."""
    pass

@womm.group()
def system():
    """🔧 System detection and prerequisites."""
    pass

@womm.group()
def deploy():
    """📦 Deployment and distribution tools."""
    pass

@womm.group()
def context():
    """🖱️ Windows context menu management."""
    pass
```

## Usage Guide

### 1. User Commands (Click CLI)
```bash
# Project creation
womm new python my-api                    # New Python project
womm new javascript --current-dir         # Setup current directory
womm new detect my-project                # Auto-detect project type

# Code quality
womm lint python --fix                    # Fix Python code issues
womm lint all ./src                       # Lint all code in src/

# Spell checking
womm spell install                        # Install CSpell globally
womm spell setup my-project --type=python # Setup for project
womm spell check --fix                    # Interactive spell fix

# System management
womm system detect --export=report.json   # System detection
womm system install python node git npm   # Install prerequisites

# Deployment
womm deploy tools --global                # Deploy to global directory
```

### 2. System Commands (CLI Manager)
```python
from shared.cli_manager import run_command

# For script development - internal use
result = run_command(["git", "status"], "Checking Git status")
if result.success:
    print("Git OK")
```

### 3. Tool Verification
```python
from shared.cli_manager import check_tool_available, get_tool_version

if check_tool_available("docker"):
    version = get_tool_version("docker")
    print(f"Docker {version} available")
```

### 4. Advanced Configuration
```python
from shared.cli_manager import CLIManager

# Custom instance
cli = CLIManager(
    default_cwd="/path/to/project",
    verbose=False,
    timeout=30
)

result = cli.run(["make", "build"], "Building project")
```

## 🎨 Logging and Display

### Log Format
```
🔍 Installing npm dependencies...
Command: npm install --save-dev eslint
Directory: /path/to/project
✅ Installing npm dependencies - SUCCESS

🔍 Checking Python...  
Command: python --version
❌ Checking Python - FAILED (code: 1)
Error: command not found
```

### Emojis Used
- 🔍 Execution in progress
- ✅ Success
- ❌ Failure
- ⚠️ Warning
- ⏱️ Timeout

## 🔧 Configuration

### Environment Variables
The CLI Manager respects standard environment variables:
- `PATH` - Executable search
- `PYTHONPATH` - Python modules
- `HOME` - User home directory

### Custom Settings
```python
# Custom CLI Manager instance
cli = CLIManager(
    default_cwd="/custom/path",
    verbose=True,
    timeout=60,
    shell=True
)
```

## 🔄 Migration Status

### ✅ Completed Migrations
- `shared/system_detector.py` - Uses `run_silent()` from CLI Manager
- All Click CLI commands - Use `run_command()` for system calls

### 🔄 In Progress
- Documentation updates for new CLI structure
- Testing of all command combinations

### 📋 Planned
- Performance optimization for command execution
- Additional command groups as needed

## 🎯 Best Practices

### For CLI Development
1. **Use Click groups** for logical command organization
2. **Leverage CLI Manager** for all system command execution
3. **Provide clear help text** for all commands and options
4. **Handle errors gracefully** with user-friendly messages

### For System Commands
1. **Always use CLI Manager** instead of direct `subprocess` calls
2. **Provide descriptive messages** for command execution
3. **Handle cross-platform differences** automatically
4. **Log all command executions** for debugging

---

**This architecture ensures both excellent user experience and robust system integration! 🚀**