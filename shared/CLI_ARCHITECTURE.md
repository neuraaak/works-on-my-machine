# 🔧 CLI Architecture - Works On My Machine

## Overview

The Works On My Machine project has been refactored to use a centralized CLI system through the `shared/cli_manager.py` module. This architecture replaces scattered `subprocess.run()` calls with a consistent and robust API.

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
shared/
├── cli_manager.py          # Main CLI module
├── CLI_ARCHITECTURE.md     # This documentation
└── [other modules...]      # Use the CLI manager
```

### Main Components

#### 1. `CommandResult`
Class for command results:
```python
class CommandResult:
    returncode: int     # Return code
    stdout: str         # Standard output
    stderr: str         # Error output
    command: List[str]  # Executed command
    cwd: Path          # Execution directory
    success: bool      # True if returncode == 0
```

#### 2. `CLIManager`
Main manager:
```python
class CLIManager:
    def run(command, description, **options) -> CommandResult
    def run_silent(command, **options) -> CommandResult  
    def run_interactive(command, **options) -> CommandResult
    def check_command_available(command) -> bool
    def get_command_version(command) -> Optional[str]
```

#### 3. Convenience Functions
```python
# Global instance for simple usage
run_command(cmd, desc)      # Execution with logging
run_silent(cmd)            # Silent execution
run_interactive(cmd)       # Interactive execution
check_tool_available(tool) # Availability check
get_tool_version(tool)     # Version retrieval
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

### 1. Basic Execution
```python
from shared.cli_manager import run_command

# With automatic logging
result = run_command(
    ["git", "status"], 
    "Checking Git status"
)

if result.success:
    print("Git OK")
else:
    print(f"Git Error: {result.stderr}")
```

### 2. Silent Execution
```python
from shared.cli_manager import run_silent

# For checks without display
result = run_silent(["npm", "--version"])
if result.success:
    version = result.stdout.strip()
```

### 3. Interactive Execution
```python
from shared.cli_manager import run_interactive

# For commands requiring user interaction
result = run_interactive(["npm", "init"])
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