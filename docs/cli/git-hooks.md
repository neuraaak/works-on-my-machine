# Git Hooks

This project uses custom Git hooks to automate code quality checks and version tag management.

## Configuration

Git hooks are configured to use the `.hooks` folder at the project root:

```bash
git config core.hooksPath .hooks
```

## Available Hooks

### Pre-commit Hook

**File:** `.hooks/pre-commit`

**Function:** Executes code quality checks before each commit.

**Actions:**

- Verifies existence of `lint.py` and Python
- Executes `python lint.py --check-only`
- Prevents commit if linting errors are detected

**Help Messages:**

- Displays commands to automatically fix issues
- Provides instructions for detailed output

### Post-commit Hook

**File:** `.hooks/post-commit`

**Function:** Automatically manages version tags after each commit.

**Actions:**

- Reads version from `pyproject.toml` (or `setup.py` as fallback)
- Creates exact version tag (`v{version}`)
- Creates major version tag (`v{major}-latest`)
- Moves existing tags if necessary
- Pushes tags to remote

## Automatic Tag System

### Exact Version Tags

Format: `v{version}`

Examples:

- `v2.6.1`
- `v3.1.0`
- `v1.0.0`

**Behavior:**

- Automatically created after each commit
- If tag already exists, it is moved to the new commit
- Allows easy retrieval of the exact commit for a version

### Major Version Tags

Format: `v{major}-latest`

Examples:

- `v2-latest`
- `v3-latest`
- `v1-latest`

**Behavior:**

- Automatically created after each commit
- Always moved to the latest commit of the major version
- Allows easy retrieval of the latest commit of a major version

## Usage Examples

### Scenario 1: New Version

```bash
# Current version: 2.6.8
git commit -m "feat: new feature"
# Result:
# - Tag v2.6.8 created on commit
# - Tag v2-latest moved to commit
```

### Scenario 2: Fix without Version Change

```bash
# Version remains 2.6.8
git commit -m "fix: bug correction"
# Result:
# - Tag v2.6.8 moved to new commit
# - Tag v2-latest moved to new commit
```

### Scenario 3: New Major Version

```bash
# Version changes to 3.1.0
git commit -m "feat: major update"
# Result:
# - Tag v3.1.0 created on commit
# - Tag v3-latest created on commit
# - Tag v2-latest remains on last v2.x commit
```

## Cross-Platform Compatibility

The system uses Bash which works on all platforms:

- **Windows:** Git Bash, WSL, or MSYS2
- **Unix/Linux/macOS:** Native Bash

### Script Files

- `.hooks/pre-commit`: Code quality verification script
- `.hooks/post-commit`: Automatic tag management script

## Error Handling

### Pre-commit Hook Errors

- **Linting error:** Commit blocked with fix instructions
- **Python missing:** Commit blocked
- **lint.py missing:** Commit blocked

### Post-commit Hook Errors

- **Version not found:** Error displayed, no tag created
- **Git not available:** Error displayed
- **Push failure:** Warning displayed

## Customization

### Temporarily Disable

```bash
# Disable pre-commit
git commit --no-verify -m "message"

# Disable post-commit
# The hook runs automatically, no option to disable it
```

### Modify Linting Exclusions

Edit `lint.py` to modify excluded folders:

```python
exclude_dirs = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "*.egg-info",
    ".venv",
    "venv",
    "node_modules",
    ".hooks",  # Exclude Git hooks
}
```

### Modify Tag Format

Edit scripts in `.hooks/` to change tag format:

- **Exact version:** Modify the `$versionTag` variable
- **Major version:** Modify the `$majorTag` variable

## Troubleshooting

### Common Issues

1. **Hooks not executing:**

   ```bash
   git config core.hooksPath .hooks
   ```

2. **Permission denied:**

   ```bash
   chmod +x .hooks/*
   ```

3. **Tags not created:**
   - Verify that version is in `pyproject.toml`
   - Verify that Git is configured with a remote

4. **Bash errors:**
   - Verify that Git Bash is installed (Windows)
   - Verify execution permissions

### Logs and Debug

Hooks display detailed messages with emojis for easy tracking:

- 🔍: Start of checks
- 🔧: Tool execution
- ✅: Success
- ❌: Error
- ⚠️: Warning
- 🔄: Action in progress
- 📤: Push to remote
- 🏷️: Tag management
