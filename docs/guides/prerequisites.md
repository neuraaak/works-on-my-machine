# Prerequisites Guide

System requirements and prerequisite tools needed for WOMM and project development.

## System Requirements

### Operating Systems

WOMM supports:

- **Windows** 10/11 (x64)
- **macOS** 10.15+ (Catalina and later)
- **Linux** - Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch Linux

### Hardware Requirements

**Minimum:**

- 2 GB RAM
- 1 GB free disk space
- Internet connection (for package downloads)

**Recommended:**

- 4 GB+ RAM
- 5 GB+ free disk space
- Fast internet connection

## Required Tools

### Python

**Minimum Version:** Python 3.10

**Installation:**

**Windows:**

```powershell
# Download from python.org
# Or use Microsoft Store
winget install Python.Python.3.11
```

**macOS:**

```bash
# Using Homebrew
brew install python@3.11
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3-pip

# Fedora
sudo dnf install python3.11

# Arch
sudo pacman -S python
```

**Verify:**

```bash
python --version  # Should show 3.10+
pip --version
```

### pip (Python Package Manager)

Usually comes with Python. If not:

```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Install
python get-pip.py

# Verify
pip --version
```

### Git

**Installation:**

**Windows:**

```powershell
# Download from git-scm.com
# Or use winget
winget install Git.Git
```

**macOS:**

```bash
# Using Homebrew
brew install git

# Or Xcode Command Line Tools
xcode-select --install
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt install git

# Fedora
sudo dnf install git

# Arch
sudo pacman -S git
```

**Configuration:**

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Optional Tools

### Node.js and npm

#### Required for JavaScript projects

**Minimum Version:** Node.js 16+

**Installation:**

**Windows:**

```powershell
# Download from nodejs.org
# Or use winget
winget install OpenJS.NodeJS
```

**macOS:**

```bash
brew install node
```

**Linux:**

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Fedora
sudo dnf install nodejs npm

# Arch
sudo pacman -S nodejs npm
```

**Verify:**

```bash
node --version
npm --version
```

### Docker

#### Optional - For containerization

**Installation:**

- **Windows/macOS:** Docker Desktop
- **Linux:** Docker Engine

**Resources:**

- [Docker Installation](https://docs.docker.com/get-docker/)

### VSCode

#### Recommended IDE

**Installation:**

**Windows:**

```powershell
winget install Microsoft.VisualStudioCode
```

**macOS:**

```bash
brew install --cask visual-studio-code
```

**Linux:**

```bash
# Download from code.visualstudio.com
# Or use snap
sudo snap install code --classic
```

**Extensions:**

- Python
- Pylance
- ESLint
- Prettier

### WSL (Windows Subsystem for Linux)

#### Windows only - Optional but recommended

**Installation:**

```powershell
# Run as Administrator
wsl --install

# Restart computer
# Install Ubuntu from Microsoft Store
```

**Benefits:**

- Better Unix tool compatibility
- Improved performance for some tasks
- Linux development environment on Windows

## Platform-Specific Prerequisites

### Windows

**Required:**

- Windows 10 version 1903+ or Windows 11
- Microsoft C++ Build Tools (for some Python packages)

**Install Build Tools:**

```powershell
# Visual Studio Build Tools
# Download from visualstudio.microsoft.com
# Select "C++ build tools" workload
```

### macOS

**Required:**

- Xcode Command Line Tools

**Installation:**

```bash
xcode-select --install
```

### Linux

**Required packages:**

**Ubuntu/Debian:**

```bash
sudo apt install build-essential python3-dev
```

**Fedora:**

```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel
```

**Arch:**

```bash
sudo pacman -S base-devel
```

## Verification

### Check All Prerequisites

```bash
# Python
python --version

# pip
pip --version

# Git
git --version

# Node.js (if needed)
node --version
npm --version

# WOMM (after installation)
womm --version
```

### System Information

```bash
# Using WOMM
womm system info

# Shows:
# - OS version
# - Python version
# - Installed tools
# - PATH configuration
```

## Troubleshooting

### Command Not Found

**Issue:** `command not found: python` or similar

**Solution:**

1. Verify installation
2. Check PATH environment variable
3. Restart terminal
4. Reinstall if necessary

### Permission Errors

**Unix/Linux:**

```bash
# Don't use sudo with pip
# Use --user flag instead
pip install --user works-on-my-machine

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install works-on-my-machine
```

### Python Version Issues

**Issue:** Multiple Python versions installed

**Solution:**

```bash
# Unix - Use specific version
python3.11 --version
python3.11 -m pip --version

# Windows - Use py launcher
py -3.11 --version
py -3.11 -m pip --version
```

## Next Steps

After installing prerequisites:

1. **Install WOMM:**

   ```bash
   pip install works-on-my-machine
   ```

2. **Follow Getting Started:**
   - [Getting Started Guide](../getting-started.md)

3. **Setup Environment:**
   - [Environment Setup Guide](environment.md)

4. **Start Development:**
   - [Configuration Guide](configuration.md)

## See Also

- [Getting Started](../getting-started.md) - Installation and first steps
- [Environment Setup](environment.md) - Development environment
- [Configuration Guide](configuration.md) - Configuration options
- [Development Guide](development.md) - Contributing

---

Ready to install WOMM? Make sure all prerequisites are installed first! ✅
