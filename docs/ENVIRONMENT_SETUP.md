# ⚙️ Environment Setup Guide

[🏠 Main](../README.md) > [📚 Documentation](README.md) > [⚙️ Environment Setup](ENVIRONMENT_SETUP.md)

[← Back to Main Documentation](../README.md)

> **Complete development environment setup with automatic PATH backup**  
> Safe installation process with recovery options for system PATH management

## 📚 Documentation Navigation

**🏠 [Main Documentation](../README.md)**  
**📚 [Documentation Index](README.md)**  
**⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)** (You are here)  
**🔧 [Common Commands](COMMON_COMMANDS.md)**  
**📋 [Documentation Rules](DOCUMENTATION_RULES.md)**  
**🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)**

## Table of Contents
- [Installation Process](#installation-process)
- [PATH Backup & Recovery](#path-backup--recovery)
- [CLI Commands](#cli-commands)
- [Manual Installation](#manual-installation)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)
- [Security Features](#security-features)
- [Related Documentation](#related-documentation)

## Related Documentation
- **🔧 [Common Commands](COMMON_COMMANDS.md)** - Standard commands and workflows
- **🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)** - Required tools installation
- **📋 [Main README](../README.md)** - Project overview and installation

## 🚀 Installation Process

### Automatic Installation Flow

The installation process follows a **safe, step-by-step approach** with automatic PATH backup:

```bash
# Start installation
python init

# Process flow:
# 1. Copy womm directory to ~/.womm
# 2. ✅ BACKUP current user PATH to ~/.womm/.backup/.path
# 3. Check and install prerequisites
# 4. Configure system PATH
# 5. Create symbolic links
# 6. Verify installation
```

### Step-by-Step Breakdown

#### 1. **Directory Copy**
- Copies the entire `works-on-my-machine` directory to `~/.womm`
- Preserves all files, configurations, and templates
- Creates the base installation directory

#### 2. **🔐 PATH Backup (Critical Safety Step)**
- **Automatic backup** of current user PATH before any modifications
- **Location**: `~/.womm/.backup/.path`
- **Format**: Timestamped backup with metadata
- **Safety**: Ensures recovery point if PATH gets corrupted

#### 3. **Prerequisites Check**
- Validates Python installation (3.8+)
- Checks for required system tools
- Installs missing dependencies if needed

#### 4. **System Configuration**
- Adds `~/.womm` to system PATH
- Creates symbolic links for easy access
- Configures shell profiles (Unix systems)

#### 5. **Verification**
- Tests all installed components
- Validates PATH configuration
- Confirms successful installation

## 🔐 PATH Backup & Recovery

### Automatic Backup System

The installation process includes **automatic PATH backup** to prevent data loss:

#### Backup Location
```
~/.womm/
└── .backup/
    ├── .path                    # Symlink to latest backup
    ├── .path_20241201_143022   # Timestamped backup file
    ├── .path_20241201_143045   # Previous backup
    └── ...
```

#### Backup Content
```bash
# Example backup file content
# PATH backup created on 2024-12-01T14:30:22
# Platform: Windows
# Original PATH:
C:\Windows\system32;C:\Windows;C:\Users\username\AppData\Local\Programs\Python\Python39\Scripts\;C:\Users\username\AppData\Local\Programs\Python\Python39\;...
```

### Recovery Commands

#### Restore PATH from Backup
```bash
# Restore PATH to last backup
womm restore-path

# Restore from specific directory
womm restore-path --target /custom/path
```

#### View Backup Information
```bash
# Show backup details
womm backup-info

# Display available backups
womm backup-info --target ~/.womm
```

### Manual Recovery (If CLI Commands Fail)

#### Windows Recovery
```cmd
# View current PATH
reg query "HKCU\Environment" /v PATH

# Restore from backup file
reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "ORIGINAL_PATH_VALUE" /f
```

#### Unix/Linux Recovery
```bash
# View backup content
cat ~/.womm/.backup/.path

# Manually update shell profile
# Edit ~/.bashrc, ~/.zshrc, or ~/.profile
export PATH="ORIGINAL_PATH_VALUE:$PATH"
```

## 🛠️ CLI Commands

### Installation Commands

```bash
# Standard installation
python init

# Installation with options
python init --no-prerequisites    # Skip prerequisite check
python init --target /custom/path # Custom installation directory
```

### PATH Management Commands

```bash
# Restore PATH from backup
womm restore-path

# View backup information
womm backup-info

# Check installation status
womm status
```

### Environment Commands

```bash
# Setup Python environment
womm env setup python

# Setup JavaScript environment  
womm env setup javascript

# Auto-detect and setup
womm env setup auto

# Validate environment
womm env validate
```

## 📋 Manual Installation

### Prerequisites

#### System Requirements
- **Python 3.8+** installed and accessible
- **Administrator privileges** (Windows) or **sudo access** (Unix)
- **Internet connection** for dependency downloads

#### Optional Tools
- **Git** for version control integration
- **VSCode** for enhanced development experience
- **Node.js** for JavaScript project support

### Step-by-Step Manual Installation

#### 1. **Download and Extract**
```bash
# Clone or download the repository
git clone <repository-url>
cd works-on-my-machine
```

#### 2. **Run Installation**
```bash
# Execute installation script
python init

# Or run directly
python womm.py install
```

#### 3. **Verify Installation**
```bash
# Test womm command
womm --help

# Check PATH configuration
echo $PATH  # Unix
echo %PATH% # Windows
```

### Custom Installation Options

#### Custom Target Directory
```bash
# Install to custom location
python init --target /opt/womm

# Verify custom installation
ls /opt/womm
```

#### Skip Prerequisites
```bash
# Install without prerequisite check
python init --no-prerequisites

# Manual prerequisite installation
python shared/installation/prerequisite_installer.py
```

## ✅ Post-Installation

### Verification Steps

#### 1. **Command Availability**
```bash
# Test womm command
womm --version

# Test subcommands
womm env --help
womm restore-path --help
```

#### 2. **PATH Configuration**
```bash
# Check if ~/.womm is in PATH
which womm  # Unix
where womm  # Windows
```

#### 3. **Backup Verification**
```bash
# Verify backup was created
ls ~/.womm/.backup/

# Check backup content
womm backup-info
```

### Configuration

#### Shell Profile Setup (Unix)
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.womm:$PATH"

# Reload shell configuration
source ~/.bashrc
```

#### Windows Registry (Automatic)
- Installation automatically configures Windows Registry
- No manual configuration required
- Restart terminal to apply changes

### First Project Setup

#### Create New Project
```bash
# Python project
womm new python my-project

# JavaScript project  
womm new javascript my-project

# Auto-detect project type
womm new auto my-project
```

#### Configure Existing Project
```bash
# Setup environment for existing project
cd existing-project
womm env setup auto
```

## 🚨 Troubleshooting

### Common Installation Issues

#### PATH Corruption
```bash
# Symptoms: womm command not found after installation
# Solution: Restore from backup
womm restore-path

# If backup command fails, manual recovery:
# Windows: Use reg command with backup content
# Unix: Edit shell profile with backup content
```

#### Permission Errors
```bash
# Windows: Run as Administrator
# Unix: Use sudo
sudo python init

# Or install to user directory
python init --target ~/.local/womm
```

#### Prerequisite Failures
```bash
# Skip prerequisites and install manually
python init --no-prerequisites

# Manual prerequisite installation
python shared/installation/prerequisite_installer.py
```

### Backup Issues

#### Missing Backup Directory
```bash
# Check if backup was created
ls ~/.womm/.backup/

# If missing, create manual backup
mkdir -p ~/.womm/.backup
echo $PATH > ~/.womm/.backup/.path_manual
```

#### Corrupted Backup Files
```bash
# View backup content
cat ~/.womm/.backup/.path

# If corrupted, use system PATH
echo $PATH > ~/.womm/.backup/.path_recovery
```

### Recovery Procedures

#### Complete Reinstallation
```bash
# Uninstall current installation
womm uninstall

# Clean up manually if needed
rm -rf ~/.womm

# Reinstall
python init
```

#### PATH Recovery
```bash
# Automatic recovery
womm restore-path

# Manual recovery (Windows)
reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "DEFAULT_PATH" /f

# Manual recovery (Unix)
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
```

## 🔒 Security Features

### Input Validation

#### Path Validation
- All user-provided paths are validated
- Prevents directory traversal attacks
- Ensures safe file operations

#### Command Validation
- External commands are validated before execution
- Prevents command injection attacks
- Uses secure subprocess execution

### Backup Security

#### Secure Backup Location
- Backups stored in protected `.backup` directory
- Timestamped files prevent overwrites
- Symlink system ensures latest backup access

#### Backup Content Protection
- No sensitive data in backup files
- Only PATH information stored
- Metadata includes platform and timestamp

### Installation Security

#### Safe File Operations
- All file operations use secure methods
- Temporary directories for sensitive operations
- Proper cleanup after installation

#### Privilege Management
- Minimal privilege requirements
- User directory installation preferred
- Clear permission requirements documented

---

**⚙️ This environment setup ensures safe, reliable installation with automatic recovery options for system PATH management.**