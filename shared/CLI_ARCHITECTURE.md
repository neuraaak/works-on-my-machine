# 🔧 CLI Architecture - Works On My Machine

## Overview

The Works On My Machine project uses a **dual CLI architecture**:
1. **User-facing CLI** with Click (`wom.py`) - Modern, user-friendly command interface
2. **System command manager** (`shared/cli_manager.py`) - Centralized subprocess execution

This architecture provides both excellent UX and robust system command handling.

## 🎯 Objectives

### ✅ Problems Solved
- **Inconsistency**: Each file handled subprocess differently
- **Inconsistent Logging**: Variable display formats
- **Error Handling**: Different treatments across files
- **Cross-platform**: Duplicated code for Windows/Linux/macOS
- **Maintenance**: Changes to be repeated in multiple files

### ✅ Benefits Provided
- **Unified API**: A single way to execute commands
- **Automatic Logging**: Consistent format with emojis and colors
- **Centralized Management**: Timeout, encoding, error handling
- **Multiple Modes**: Silent, interactive, verbose
- **Simplified Maintenance**: Single source of truth

## 🏗️ Architecture

### File Structure
```
works-on-my-machine/
├── wom.py                  # Main CLI entry point (Click)
├── shared/
│   ├── cli_manager.py      # System command manager
│   ├── CLI_ARCHITECTURE.md # This documentation
│   └── [other modules...]  # Use the CLI manager
└── languages/              # Language-specific tools
```

### Main Components

#### 1. Click CLI (`wom.py`)
Modern command-line interface:
```bash
# Main commands
wom new python my-project          # Create Python project
wom new javascript --type=react    # Create React project
wom lint python --fix             # Lint and fix Python code
wom spell check ./src              # Spell check files
wom system install python node    # Install prerequisites
```

#### 2. System Command Manager (`cli_manager.py`)
Centralized subprocess execution:
```python
class CLIManager:
    def run(command, description, **options) -> CommandResult
    def run_silent(command, **options) -> CommandResult  
    def run_interactive(command, **options) -> CommandResult
    def check_command_available(command) -> bool
    def get_command_version(command) -> Optional[str]
```

#### 3. Command Groups Structure
```python
@click.group()
def wom():              # Main entry point
    pass

@wom.group()
def new():              # Project creation
    pass

@wom.group() 
def lint():             # Code quality
    pass

@wom.group()
def spell():            # Spell checking
    pass
```

## 🔄 Completed Migration

### Refactored Files
- ✅ `lint.py` - Main linting script
- ✅ `languages/python/scripts/lint.py` - Python linting
- ✅ `shared/project_detector.py` - Project detection
- ✅ `shared/cspell_manager.py` - CSpell management
- ✅ `shared/prerequisite_installer.py` - Prerequisites installation
- ✅ `shared/environment_manager.py` - Environment management
- ✅ `shared/system_detector.py` - System detection (migrated)
- ✅ `init.py` - Initialization script

### Migration Patterns

#### Before (direct subprocess)
```python
import subprocess

try:
    result = subprocess.run(
        ["python", "--version"], 
        capture_output=True, 
        text=True, 
        check=True
    )
    print(f"Python: {result.stdout}")
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
```

#### After (CLI Manager)
```python
from shared.cli_manager import run_command

result = run_command(["python", "--version"], "Python version check")
if result.success:
    print(f"Python: {result.stdout}")
else:
    print(f"Error: {result.stderr}")
```

## 💡 Usage Guide

### 1. User Commands (Click CLI)
```bash
# Project creation
wom new python my-api                    # New Python project
wom new javascript --current-dir         # Setup current directory
wom new detect my-project                # Auto-detect project type

# Code quality
wom lint python --fix                    # Fix Python code issues
wom lint all ./src                       # Lint all code in src/

# Spell checking
wom spell install                        # Install CSpell globally
wom spell setup my-project --type=python # Setup for project
wom spell check --fix                    # Interactive spell fix

# System management
wom system detect --export=report.json   # System detection
wom system install python node git       # Install prerequisites

# Deployment
wom deploy tools --global                # Deploy to global directory
```

### 2. System Commands (CLI Manager)
```python
from shared.cli_manager import run_command

# For script development - internal use
result = run_command(["git", "status"], "Checking Git status")
if result.success:
    print("Git OK")
```

### 4. Tool Verification
```python
from shared.cli_manager import check_tool_available, get_tool_version

if check_tool_available("docker"):
    version = get_tool_version("docker")
    print(f"Docker {version} available")
```

### 5. Advanced Configuration
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
- `NODE_PATH` - Node.js modules

### Timeouts
- Default: No timeout
- Configurable per command
- Clean timeout handling

### Encoding
- UTF-8 by default
- Error handling for encoding
- Cross-platform (Windows CP1252, Unix UTF-8)

## 🧪 Testing and Validation

### Manual Tests Completed
- ✅ Execution on Windows 10
- ✅ Python commands (pip, python)
- ✅ Node.js commands (npm, npx)
- ✅ Git commands
- ✅ Error handling
- ✅ Timeouts

### To Be Tested
- [ ] Linux (Ubuntu, CentOS)
- [ ] macOS
- [ ] Commands with special characters
- [ ] Very long outputs
- [ ] Complex interactive commands

## 🔮 Future Developments

### Planned Features
- **Result Caching**: Avoid identical re-executions
- **Parallelization**: Simultaneous command execution
- **History**: Persistent command logging
- **Metrics**: Execution time, statistics
- **Automatic Retry**: New attempt on failure

### Possible Optimizations
- **Lazy Loading**: On-demand module imports
- **Validation**: Command syntax verification
- **Suggestions**: Similar commands on error
- **Auto-completion**: Interactive shell support

## 📋 Maintenance

### Best Practices
1. **Always** use `run_command()` with description
2. **Prefer** `run_silent()` for checks
3. **Verify** `result.success` before accessing stdout/stderr
4. **Document** complex commands
5. **Test** on different platforms

### Debugging
```python
# Enable verbose logging
from shared.cli_manager import CLIManager
cli = CLIManager(verbose=True)

# Inspect detailed result
result = cli.run(cmd, desc)
print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")
```

---

*This CLI architecture improves the robustness, maintainability, and user experience of Works On My Machine by centralizing and standardizing all system interactions.*