# Windows Context Menu Registrator

## Overview

The `registrator.py` system allows users to add their own scripts and tools to the Windows context menu for quick access from any folder. This is a standalone utility that can be used independently of WOMM.

## Features

- **Multi-format support**: Python, PowerShell, Batch, and Executable files
- **Auto-detection**: Automatically detects script type and configures appropriate execution
- **Icon management**: Automatic icon assignment or custom icon support
- **Backup/Restore**: Full backup and restore functionality for context menu entries
- **Validation**: Comprehensive validation of scripts and paths
- **Registry management**: Safe addition and removal of context menu entries

## Usage

### Basic Usage

```bash
# Add a Python script to context menu
python shared/system/registrator.py "C:\tools\my_script.py" "My Python Action"

# Add a PowerShell script
python shared/system/registrator.py "C:\tools\deploy.ps1" "Deploy Project"

# Add a batch file
python shared/system/registrator.py "C:\tools\build.bat" "Build Project"
```

### Advanced Usage

```bash
# Add with custom icon
python shared/system/registrator.py "C:\tools\script.py" "Custom Action" "powershell"

# Add with auto-detected icon
python shared/system/registrator.py "C:\tools\script.py" "Auto Action" "auto"

# Dry run (test without making changes)
python shared/system/registrator.py "C:\tools\script.py" "Test Action" --dry-run
```

### Management Commands

```bash
# List all context menu entries
python shared/system/registrator.py --list

# Remove an entry by key name
python shared/system/registrator.py --remove womMyScript

# Backup current context menu entries
python shared/system/registrator.py --backup "my_backup.json"

# Restore from backup
python shared/system/registrator.py --restore "my_backup.json"
```

## Supported File Types

| Extension | Type | Default Icon | Execution Method |
|-----------|------|--------------|------------------|
| `.py` | Python | `py.exe` | `python script.py "%V"` |
| `.ps1` | PowerShell | `powershell.exe` | `powershell.exe -ExecutionPolicy Bypass -File script.ps1 "%V"` |
| `.bat` | Batch | `cmd.exe` | `cmd.exe /c script.bat "%V"` |
| `.cmd` | Batch | `cmd.exe` | `cmd.exe /c script.cmd "%V"` |
| `.exe` | Executable | File's own icon | `script.exe "%V"` |

## Icon Options

### Predefined Icons

- `"python"` - Python executable icon
- `"powershell"` - PowerShell icon
- `"cmd"` - Command prompt icon
- `"auto"` - Auto-detect based on file type

### Custom Icons

You can specify any `.exe` or `.ico` file path:

```bash
python shared/system/registrator.py "C:\tools\script.py" "My Action" "C:\icons\my_icon.exe"
```

## Registry Structure

The registrator creates entries in two locations:

1. **File context menu**: `Software\Classes\Directory\shell\{key_name}`
2. **Background context menu**: `Software\Classes\Directory\background\shell\{key_name}`

### Registry Key Naming

Keys are automatically generated from the script filename:
- `my_script.py` → `womMyScript`
- `deploy.ps1` → `womDeploy`
- `build.bat` → `womBuild`

## Examples

### Example 1: Python Development Script

```bash
# Create a Python script for project setup
echo "import sys; print(f'Setting up project in: {sys.argv[1]}')" > C:\tools\setup_project.py

# Add to context menu
python shared/system/registrator.py "C:\tools\setup_project.py" "Setup Project"
```

### Example 2: PowerShell Deployment Script

```bash
# Create a PowerShell deployment script
echo "Write-Host 'Deploying to: ' + $args[0]" > C:\tools\deploy.ps1

# Add to context menu with PowerShell icon
python shared/system/registrator.py "C:\tools\deploy.ps1" "Deploy" "powershell"
```

### Example 3: Batch Build Script

```bash
# Create a batch build script
echo "@echo off" > C:\tools\build.bat
echo "echo Building project in: %1" >> C:\tools\build.bat

# Add to context menu
python shared/system/registrator.py "C:\tools\build.bat" "Build Project"
```

## Backup and Restore

### Creating Backups

```bash
# Backup all context menu entries
python shared/system/registrator.py --backup "context_menu_backup.json"
```

### Restoring from Backup

```bash
# Restore context menu entries
python shared/system/registrator.py --restore "context_menu_backup.json"
```

### Backup File Format

Backup files are JSON format containing all registry entries:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "entries": [
    {
      "key": "womMyScript",
      "title": "My Python Action",
      "command": "python \"C:\\tools\\my_script.py\" \"%V\"",
      "icon": "C:\\Windows\\py.exe"
    }
  ]
}
```

## Error Handling

### Common Issues

1. **Script not found**: Ensure the script path is correct and accessible
2. **Permission denied**: Run as administrator for registry modifications
3. **Invalid icon**: Use valid `.exe` or `.ico` files for custom icons
4. **Script type not supported**: Use `.py`, `.ps1`, `.bat`, `.cmd`, or `.exe` files

### Validation

The registrator validates:
- Script file existence
- Script file permissions
- Icon file existence (if custom)
- Registry access permissions
- Command syntax

## Security Considerations

- Only add scripts you trust to the context menu
- Scripts receive the selected folder path as an argument (`%V`)
- Use `--dry-run` to test before making changes
- Regular backups help recover from issues

## Integration with WOMM

While the registrator is independent, it can be used with WOMM:

1. **Custom project scripts**: Add your own project setup scripts
2. **Development tools**: Integrate external development tools
3. **Deployment scripts**: Add deployment automation scripts
4. **Utility scripts**: Add frequently used utility scripts

## Troubleshooting

### Script Not Appearing in Context Menu

1. Check if the script was added successfully: `python registrator.py --list`
2. Verify the registry key exists
3. Restart Windows Explorer: `taskkill /f /im explorer.exe && start explorer.exe`
4. Check for permission issues

### Script Execution Errors

1. Verify the script works when run directly
2. Check if required dependencies are available
3. Ensure the script handles the `%V` argument correctly
4. Test with `--dry-run` first

### Registry Issues

1. Use backup/restore functionality
2. Check Windows Registry permissions
3. Run as administrator if needed
4. Use Windows Registry Editor to manually verify entries

## Best Practices

1. **Use descriptive titles**: Make context menu entries clear and meaningful
2. **Test scripts first**: Ensure scripts work before adding to context menu
3. **Regular backups**: Create backups before making changes
4. **Organize scripts**: Keep scripts in a dedicated tools directory
5. **Document scripts**: Document what each script does
6. **Use appropriate icons**: Choose icons that represent the script's function
7. **Handle arguments**: Ensure scripts properly handle the `%V` folder argument