# 🛠️ Prerequisites Installation Manager

The Works On My Machine system includes a **smart prerequisites installation manager** that automates the installation of Python, Node.js, and Git according to your platform.

## 🎯 **Features**

### ✅ **Automatic Detection**
- **OS**: Windows, macOS, Linux
- **Package Managers**: Chocolatey, Winget, Scoop, Homebrew, APT, DNF, etc.
- **Versions**: Minimum version verification
- **Environments**: VS Code, shells, etc.

### 🚀 **Smart Installation**
- **Hierarchy**: Chocolatey → Winget → Scoop → Manual installation
- **Robust fallback**: If one manager fails, tries the next
- **Manager installation**: Offers to install Chocolatey/Homebrew
- **Custom locations**: Choice of installation directory

### 🤔 **Interactive Mode**
- **Prompt during init**: Offers installation of missing prerequisites
- **User choice**: Can refuse and continue anyway
- **Detailed feedback**: Real-time progress and results

## 📋 **Usage**

### **Automatic Integration**
```bash
# During installation
python womm.py install
# → Automatically detects missing prerequisites
# → Offers to install them
```

### **Dedicated Commands**
```bash
# Check only
dev-tools-install --check

# Specific installation
dev-tools-install --install python node git npm
dev-tools-install --install all

# Interactive mode
dev-tools-install --interactive

# Custom location
dev-tools-install --install python --path "C:/Dev/Python"
```

### **System Diagnostics**
```bash
# Complete system report
python shared/system_detector.py --summary
python shared/system_detector.py --export system_report.json
```

## 🌍 **Support Multi-Plateforme**

### **Windows**
- **Chocolatey** (priority 1) - Installation via PowerShell
- **Winget** (priority 2) - Native Microsoft package manager
- **Scoop** (priority 3) - Developer package manager
- **Manual installation** - Direct download + silent installation

### **macOS**
- **Homebrew** (priority 1) - Installation via curl
- **MacPorts** (priority 2) - Homebrew alternative
- **Manual installation** - Direct download

### **Linux**
- **APT** (Debian/Ubuntu) - `sudo apt install`
- **DNF** (Fedora/RHEL) - `sudo dnf install`
- **YUM** (CentOS) - `sudo yum install`
- **Pacman** (Arch) - `sudo pacman -S`
- **Snap** (Universal) - `sudo snap install`

## ⚙️ **Configuration**

### **Detected Prerequisites**
| Tool | Min Version | Description |
|------|-------------|-------------|
| **Python** | 3.8+ | Works On My Machine scripts and Python tools |
| **Node.js** | 18+ | CSpell, JavaScript projects, npm |
| **Git** | 2.0+ | Version control (optional) |

### **Package Managers**
| Platform | Manager | Installation |
|----------|---------|--------------|
| Windows | Chocolatey | Automatic PowerShell |
| Windows | Winget | Pre-installed Windows 10+ |
| Windows | Scoop | Automatic detection |
| macOS | Homebrew | Automatic curl |
| Linux | APT/DNF/YUM | Distribution detection |

## 🔧 **Installation Workflow**

```
1. 🔍 OS + Architecture Detection
2. 📦 Scan available package managers
3. ✅ Check existing prerequisites
4. 🤔 User prompt (if missing)
5. 🛠️ Install package manager (if needed)
6. 📥 Install missing prerequisites
7. 🔄 Post-installation verification
8. ✅ Automatic PATH configuration
```

## 💡 **Usage Examples**

### **Scenario 1: First Use**
```bash
python womm.py install
```
```
🔍 Checking prerequisites...
✅ PYTHON: 3.11.3 - C:\Python311\python.exe
❌ NODE: Not installed - Node.js for CSpell and JavaScript projects
✅ GIT: 2.40.0 - C:\Program Files\Git\cmd\git.exe

⚠️  Missing prerequisites: node

🤔 Do you want to install missing prerequisites? (y/N): y
📦 Available package managers: chocolatey, winget
🍫 Install Chocolatey to facilitate installations? (y/N): y
✅ Chocolatey installed
📦 Installing node via chocolatey...
✅ node installed successfully
🎉 All prerequisites have been installed successfully!
```

### **Scenario 2: Selective Installation**
```bash
dev-tools-install --install node --path "D:/NodeJS"
```
```
📦 Installing node...
📁 Custom location: D:/NodeJS
📥 Downloading Node.js...
✅ Node.js installed successfully
```

### **Scenario 3: Diagnostics**
```bash
dev-tools-install --check
```
```
✅ python: 3.11.3
✅ node: 20.9.0
✅ git: 2.40.0
```

## 🛡️ **Security**

- **Official scripts**: Uses only official installers
- **HTTPS**: Secure downloads only
- **Verification**: Post-installation version check
- **Permissions**: Asks confirmation for admin actions
- **Isolation**: Installation in dedicated directories

## 🚨 **Error Handling**

- **Missing package manager** → Offers to install one
- **Installation failure** → Tries next package manager
- **Insufficient permissions** → Clear instructions
- **Network unavailable** → Alternative suggestions
- **Insufficient disk space** → Explicit warning

## 📊 **System Statistics**

The system detector collects:
- **OS**: Type, version, architecture
- **Package managers**: Available with versions
- **Development**: Detected editors, shells
- **Recommendations**: Suggested optimizations

---

**This system makes dev-tools entirely self-sufficient! 🎉**