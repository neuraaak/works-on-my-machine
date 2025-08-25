# 🖱️ Context Menu Guide

[🏠 Main](../../README.md) > [📚 Documentation](../README.md) > [🔧 CLI Documentation](README.md) > [🖱️ Context Menu](CONTEXT.md)

[← Back to CLI Documentation](README.md)

> **Complete guide to Windows context menu integration with WOMM**  
> Integrate WOMM commands into Windows Explorer context menu

## 📚 Documentation Navigation

**🏠 [Main Documentation](../../README.md)**  
**📚 [Documentation Index](../README.md)**  
**🔧 [CLI Documentation](README.md)**  
**🖱️ [Context Menu](CONTEXT.md)** (You are here)  
**🔌 [API Documentation](../api/README.md)**

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [🔧 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🎨 Customization](#-customization)
- [🔍 Troubleshooting](#-troubleshooting)

## 🎯 Overview

WOMM provides Windows context menu integration, allowing you to access WOMM commands directly from Windows Explorer. This enables quick project creation, setup, and management without using the command line.

### ✅ **Features**
- **Project Creation** - Create new projects from context menu
- **Project Setup** - Configure existing projects
- **Template Management** - Access template commands
- **Quick Actions** - Common development tasks

### 🔄 **Context Menu Workflow**
```
Right-click → Context Menu → WOMM Commands → Project Operations → Results
```

## 🚀 Quick Start

### **Install Context Menu**
```bash
# Install context menu integration
womm context install

# Verify installation
womm context status

# Test context menu
womm context test
```

### **Basic Usage**
1. **Navigate** to a directory in Windows Explorer
2. **Right-click** in the folder
3. **Select** "WOMM" from the context menu
4. **Choose** the desired command
5. **Follow** the prompts

### **Available Commands**
- **New Project** - Create new Python/JavaScript projects
- **Setup Project** - Configure existing projects
- **Template Create** - Create template from project
- **Template Use** - Use template for new project
- **Lint Project** - Run code quality checks
- **Spell Check** - Check documentation spelling

## 🔧 Installation

### **Automatic Installation**
```bash
# Install with default settings
womm context install

# Install with custom settings
womm context install --custom

# Install for current user only
womm context install --user
```

### **Manual Installation**
```bash
# Create registry entries manually
womm context install --manual

# Install specific commands only
womm context install --commands new,setup,template

# Install with custom menu name
womm context install --menu-name "Development Tools"
```

### **Installation Options**
- `--user` - Install for current user only
- `--system` - Install for all users (requires admin)
- `--custom` - Custom installation options
- `--commands` - Specify which commands to install
- `--menu-name` - Custom menu name

### **Verification**
```bash
# Check installation status
womm context status

# Test context menu
womm context test

# List installed commands
womm context list
```

## ⚙️ Configuration

### **Context Menu Configuration**
```bash
# Configure context menu
womm context config

# Set default options
womm context config --set default-project-type python

# Configure command visibility
womm context config --set show-advanced-commands false
```

### **Configuration Options**
```yaml
# .womm-context.yml
context_menu:
  menu_name: "WOMM"
  show_advanced: false
  default_project_type: python
  commands:
    new_project: true
    setup_project: true
    template_create: true
    template_use: true
    lint_project: true
    spell_check: true
```

### **Command Configuration**
```bash
# Configure specific commands
womm context config command new --enabled true
womm context config command setup --enabled true
womm context config command template --enabled true

# Set command options
womm context config command new --default-type python
womm context config command setup --auto-detect true
```

## 🎨 Customization

### **Custom Menu Items**
```bash
# Add custom menu item
womm context add "My Custom Command" "womm custom-command"

# Add menu separator
womm context add --separator

# Add submenu
womm context add --submenu "Advanced" "womm advanced-command"
```

### **Menu Organization**
```bash
# Create submenus
womm context add --submenu "Projects" "womm new"
womm context add --submenu "Projects" "womm setup"
womm context add --submenu "Templates" "womm template create"
womm context add --submenu "Templates" "womm template use"
```

### **Icon Customization**
```bash
# Set custom icon
womm context config --icon "C:\path\to\icon.ico"

# Use default icons
womm context config --icon default

# Remove icon
womm context config --icon none
```

### **Advanced Customization**
```bash
# Create custom script
womm context add --script "custom-script.bat"

# Add PowerShell command
womm context add --powershell "Get-WOMMStatus"

# Add with parameters
womm context add "Python Project" "womm new python --interactive"
```

## 🔍 Troubleshooting

### **Installation Issues**

**Permission errors:**
```bash
# Run as administrator
# Right-click Command Prompt → Run as administrator
womm context install

# Install for current user only
womm context install --user

# Check permissions
womm context check-permissions
```

**Registry access issues:**
```bash
# Check registry access
womm context check-registry

# Repair registry entries
womm context repair

# Reset registry
womm context reset
```

### **Context Menu Issues**

**Menu not appearing:**
```bash
# Refresh context menu
womm context refresh

# Restart Explorer
taskkill /f /im explorer.exe
start explorer.exe

# Check installation
womm context status
```

**Commands not working:**
```bash
# Test commands
womm context test

# Check command paths
womm context check-paths

# Repair commands
womm context repair-commands
```

### **Configuration Issues**

**Config not loading:**
```bash
# Check config file
womm context config --show

# Reset configuration
womm context config --reset

# Create default config
womm context config --init
```

**Custom commands not working:**
```bash
# Validate custom commands
womm context validate

# Test custom command
womm context test --command "custom-command"

# Debug custom command
womm context debug --command "custom-command"
```

### **Performance Issues**

**Slow context menu:**
```bash
# Optimize context menu
womm context optimize

# Disable unused commands
womm context config --set show-advanced-commands false

# Use lightweight commands
womm context config --set use-lightweight true
```

**Memory usage:**
```bash
# Check memory usage
womm context memory

# Optimize memory
womm context optimize --memory

# Clean up cache
womm context cleanup
```

### **Uninstallation**

**Remove context menu:**
```bash
# Remove context menu
womm context uninstall

# Remove specific commands
womm context uninstall --commands new,setup

# Remove completely
womm context uninstall --all
```

**Clean up registry:**
```bash
# Clean registry entries
womm context cleanup --registry

# Remove all WOMM entries
womm context cleanup --all

# Reset registry
womm context reset
```

### **Debug Mode**
Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
set WOMM_DEBUG=1

# Run context commands with debug output
womm context install --debug

# Check logs
type %USERPROFILE%\.womm\logs\context.log
```

### **Log Files**
WOMM creates detailed logs for troubleshooting:

```bash
# View context menu logs
type %USERPROFILE%\.womm\logs\context.log

# View installation logs
type %USERPROFILE%\.womm\logs\install.log

# View registry logs
type %USERPROFILE%\.womm\logs\registry.log
```

### **Registry Information**
Context menu entries are stored in:
- **Current User**: `HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell`
- **All Users**: `HKEY_LOCAL_MACHINE\Software\Classes\Directory\Background\shell`

### **File Locations**
- **Configuration**: `%USERPROFILE%\.womm\context.yml`
- **Scripts**: `%USERPROFILE%\.womm\scripts\`
- **Icons**: `%USERPROFILE%\.womm\icons\`
- **Logs**: `%USERPROFILE%\.womm\logs\`

---

**🖱️ This context menu guide provides comprehensive instructions for integrating WOMM commands into Windows Explorer for seamless development workflow.**
