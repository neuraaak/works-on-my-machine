# 🔧 Windows Context Menu Registrator

Enhanced Windows context menu management system for Works On My Machine, providing easy access to development tools directly from file explorer.

## 🌟 Features

### ✅ **Multi-Script Support**
- **Python scripts** (.py) - Automatic Python executable detection
- **PowerShell scripts** (.ps1) - Secure execution policy handling
- **Batch files** (.bat, .cmd) - Direct execution
- **Executables** (.exe) - Native file execution

### ✅ **Smart Auto-Detection**
- **Script type** detection from file extension
- **Icon selection** based on script type
- **Command building** optimized for each script type
- **Registry key** generation from script name

### ✅ **Advanced Management**
- **Backup/Restore** context menu entries
- **List existing** entries with details
- **Remove entries** by key name
- **Dry-run mode** for testing
- **Validation** of script paths and icons

### ✅ **Works On My Machine Integration**
- **Auto-registration** during initialization
- **Bulk operations** for WOM tools
- **Consistent naming** with "wom" prefix
- **Global commands** via bin directory

## 📁 Files Structure

```
shared/system/
├── registrator.py          # Enhanced Python version
├── registrator.ps1         # Enhanced PowerShell version
├── register_wom_tools.py   # WOM-specific bulk registrator
└── REGISTRATOR.md          # This documentation
```

## 🚀 Usage

### **Individual Script Registration**

#### Python Version
```bash
# Basic registration (auto-detection)
python registrator.py "C:\tools\my_script.py" "My Python Action"

# With custom icon
python registrator.py "C:\tools\script.ps1" "PowerShell Action" "powershell"

# Batch file with auto icon
python registrator.py "C:\tools\deploy.bat" "Deploy Project" "auto"

# Management commands
python registrator.py --list
python registrator.py --remove womMyScript
python registrator.py --backup "backup.json"
python registrator.py --restore "backup.json"
python registrator.py --dry-run "C:\tools\test.py" "Test Action"
```

#### PowerShell Version
```powershell
# Basic registration
.\registrator.ps1 "C:\tools\my_script.py" "My Python Action"

# With options
.\registrator.ps1 "C:\tools\script.ps1" "PowerShell Action" "powershell"
.\registrator.ps1 -List
.\registrator.ps1 -Remove -RemoveKey "womMyScript"
.\registrator.ps1 -Interactive
.\registrator.ps1 -DryRun "C:\tools\test.py" "Test Action"
```

### **Works On My Machine Tools Registration**

```bash
# Register all WOM tools to context menu
python register_wom_tools.py --register

# Remove all WOM tools
python register_wom_tools.py --unregister

# List registered WOM tools
python register_wom_tools.py --list

# Register without backup (faster)
python register_wom_tools.py --register --no-backup
```

### **Global Commands (after initialization)**

```bash
# Use global commands from anywhere
context-menu --register
registrator --list
context-menu --unregister
```

## ⚙️ Auto-Detection Features

### **Script Types**
| Extension | Type | Command Template | Default Icon |
|-----------|------|------------------|--------------|
| `.py` | Python | `python "script" "%V"` | `C:\Windows\py.exe` |
| `.ps1` | PowerShell | `powershell.exe -ExecutionPolicy Bypass -File "script" "%V"` | PowerShell icon |
| `.bat`, `.cmd` | Batch | `cmd.exe /c "script" "%V"` | `C:\Windows\System32\cmd.exe` |
| `.exe` | Executable | `"script" "%V"` | File's own icon |

### **Icon Keywords**
- `auto` - Auto-detect based on script type
- `powershell` or `ps` - PowerShell icon
- `python` or `py` - Python icon
- `cmd` or `batch` - Command prompt icon
- Full path to custom icon file

### **Registry Key Generation**
Script names are converted to camelCase registry keys with "wom" prefix:
- `my_script.py` → `womMyScript`
- `deploy-tools.bat` → `womDeployTools`
- `project_setup.ps1` → `womProjectSetup`

## 🛡️ Security & Validation

### **Path Validation**
- File existence checking
- Read/execute permission verification
- Supported file type validation
- Icon path validation with fallbacks

### **Registry Safety**
- User-level registry access only (HKEY_CURRENT_USER)
- Backup creation before bulk operations
- Error handling with rollback capability
- Dry-run mode for testing changes

### **PowerShell Security**
- `-ExecutionPolicy Bypass` for WOM scripts only
- Full path specification to prevent hijacking
- Proper parameter escaping

## 🎯 Registered WOM Tools

After running `register_wom_tools.py --register`, these tools become available in folder context menus:

| Tool | Description | Script |
|------|-------------|--------|
| 🛠️ Initialize Works On My Machine | Initialize WOM in current directory | `init.py` |
| 🔍 Detect Project Type | Auto-detect and setup project | `project_detector.py` |
| ⚙️ Setup Dev Environment | Configure development environment | `environment_manager.py` |
| 📦 Install Prerequisites | Install required development tools | `prerequisite_installer.py` |
| 🔧 Configure VSCode | Setup VSCode for development | `vscode_config.py` |
| 📝 Spell Check Project | Check spelling in project files | `cspell_manager.py` |

## 🔧 Integration with Init Process

During Works On My Machine initialization on Windows, users are prompted:

```
🔧 Windows System Integration
Do you want to add Works On My Machine to the context menu? (y/N):
```

- **Yes** → Automatically registers all WOM tools
- **No** → Provides manual registration instructions

## 📋 Backup & Restore

### **Automatic Backups**
- Created before bulk registrations
- Timestamped JSON format
- Stored in `.backups/` directory
- Include all context menu entries

### **Manual Backup**
```bash
python registrator.py --backup "my_backup.json"
```

### **Restore from Backup**
```bash
python registrator.py --restore "my_backup.json"
```

## 🚨 Troubleshooting

### **Permission Errors**
```
❌ Permission denied accessing registry
💡 Try running as administrator
```
**Solution**: Run PowerShell/Command Prompt as Administrator

### **Script Not Found**
```
❌ Script file does not exist: C:\path\to\script.py
```
**Solution**: Verify script path and ensure file exists

### **Python Not Found**
```
❌ Python executable not found
```
**Solution**: Install Python or ensure it's in PATH

### **Icon Missing**
```
⚠️ Icon not found: C:\custom\icon.ico
💡 Using default icon for python: C:\Windows\py.exe
```
**Solution**: Use auto-detection or provide valid icon path

### **Registry Key Conflicts**
If a registry key already exists, the registrator will overwrite it. Use `--list` to check existing entries before adding new ones.

## 💡 Best Practices

1. **Always create backups** before bulk operations
2. **Use descriptive titles** for context menu entries
3. **Test with --dry-run** before making changes
4. **Use auto-detection** for icons when possible
5. **Regular cleanup** of unused entries
6. **Check PATH** if Python scripts fail to execute

## 🔗 Related Documentation

- [Prerequisites Installation](../PREREQUISITE_INSTALLER.md) - Installing required tools
- [Environment Setup](../ENVIRONMENT_SETUP.md) - Development environment configuration
- [Project Detection](../project_detector.py) - Automatic project type detection

---

**Works On My Machine Context Menu Integration - Making development tools accessible from anywhere! 🚀**