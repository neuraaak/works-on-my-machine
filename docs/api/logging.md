# Normalized Logging Patterns

## Final Design

All logging patterns use the format: `[<color>$pattern</color>] :: $message`

## Main Patterns (kept)

| Pattern     | Color        | Usage                    | Example                                               |
| ----------- | ------------ | ------------------------ | ----------------------------------------------------- |
| `[RUN]`     | cyan         | Command execution        | `[RUN] :: Installing dependencies...`                 |
| `[ERROR]`   | red          | Critical errors          | `[ERROR] :: File not found`                           |
| `[WARN]`    | yellow       | Warnings                 | `[WARN] :: Directory already exists`                  |
| `[INFO]`    | blue         | General information      | `[INFO] :: Current location: /path`                   |
| `[OK]`      | green        | Simple success           | `[OK] :: File copied successfully`                    |
| `[SUCCESS]` | bright_green | Major success            | `[SUCCESS] :: Installation complete!`                 |
| `[FAILED]`  | bright_red   | Operation failure        | `[FAILED] :: Installation failed`                     |
| `[TIP]`     | magenta      | General tips             | `[TIP] :: Add .txt files with one word per line`      |
| `[HINT]`    | cyan         | Specific hints           | `[HINT] :: Try running with administrator privileges` |

## Grouped Patterns (Option A)

### `[FILE]` (replaces `[COPY]`, `[BACKUP]`, `[RESTORE]`)

- **Color**: blue
- **Usage**: File operations
- **Examples**:
  - `[FILE] :: Copying from: /source`
  - `[FILE] :: Backing up old version to: /backup`
  - `[FILE] :: Restoring PATH from backup...`

### `[SYSTEM]` (replaces `[BAT]`, `[EXEC]`, `[WINDOWS]`, `[REGISTER]`)

- **Color**: blue
- **Usage**: Windows system operations
- **Examples**:
  - `[SYSTEM] :: Created main womm.bat: /path`
  - `[SYSTEM] :: Created Unix womm executable: /path`
  - `[SYSTEM] :: Adding to Windows context menu...`

### `[INSTALL]` (replaces `[INSTALL]`, `[DICT]`)

- **Color**: green
- **Usage**: Installation and configuration
- **Examples**:
  - `[INSTALL] :: Installing CSpell and dictionaries...`
  - `[INSTALL] :: Installing dictionaries...`

## Specialized Patterns (kept)

| Pattern         | Color   | Usage                    | Example                                                     |
| --------------- | ------- | ------------------------ | ----------------------------------------------------------- |
| `[SECURITY]`    | red     | Security issues          | `[SECURITY] :: Command validation failed`                   |
| `[FALLBACK]`    | yellow  | Fallback mode            | `[FALLBACK] :: Trying with npx...`                          |
| `[STATUS]`      | cyan    | General status           | `[STATUS] :: CSPELL PROJECT STATUS`                         |
| `[DETECT]`      | blue    | Automatic detection      | `[DETECT] :: Project type detected: python`                 |
| `[UNKNOWN]`     | yellow  | Unknown state            | `[UNKNOWN] :: Project type not detected`                    |
| `[EVAL]`        | magenta | Evaluation               | `[EVAL] :: Will add 5 dictionaries to CSpell configuration` |
| `[CONFIRM]`     | yellow  | Confirmation request     | `[CONFIRM] :: Continue? (y/N):`                             |
| `[PROCESS]`     | blue    | Processing in progress   | `[PROCESS] :: Adding dictionary: words.txt`                 |
| `[SUMMARY]`     | cyan    | Summary                  | `[SUMMARY] :: Process completed: 3/5 dictionaries added`    |
| `[PARTIAL]`     | yellow  | Partial result           | `[PARTIAL] :: Some dictionaries added successfully`         |
| `[INTERACTIVE]` | magenta | Interactive mode         | `[INTERACTIVE] :: Interactive word addition mode`           |
| `[PREVIEW]`     | blue    | Preview                  | `[PREVIEW] :: Words to add: word1, word2, word3`            |
| `[ADDED]`       | green   | Item added               | `[ADDED] :: 'newword' added to list`                        |
| `[WORDS]`       | blue    | Words/dictionary         | `[WORDS] :: Custom words: 15`                               |
| `[CHECK]`       | yellow  | Verification             | `[CHECK] :: Checking: file.txt`                             |
| `[FIX]`         | green   | Correction               | `[FIX] :: Interactive mode - Fixing: file.txt`              |
| `[PATH]`        | cyan    | PATH configuration       | `[PATH] :: Setting up Windows USER PATH (safe mode)...`     |

## Migration from Old Format

### Before (old format)

```python
print("[COPY] Copying from: /source")
print("[BAT] Created main womm.bat: /path")
print("[ERROR] File not found")
```

### After (new format)

```python
from shared.ui.console import print_file, print_system, print_error

print_file("Copying from: /source")
print_system("Created main womm.bat: /path")
print_error("File not found")
```

## Usage

### Import Functions

```python
from shared.ui.console import (
    print_run, print_error, print_warning, print_info,
    print_file, print_system, print_install,
    print_security, print_fallback, print_status
)
```

### Direct Usage

```python
print_run("Executing command...")
print_error("Something went wrong")
print_file("Copying files...")
```

### Generic Function

```python
from shared.ui.console import print_pattern

print_pattern("CUSTOM", "Custom message")  # Custom pattern
```

## Colors by Category

- **🔴 Red**: Critical errors, security
- **🟢 Green**: Success, installations, fixes
- **🟡 Yellow**: Warnings, intermediate states, confirmations
- **🔵 Blue**: Information, system operations, processing
- **🟣 Magenta**: Tips, interactions, evaluations
- **🔵 Cyan**: Active actions, summaries, detection
