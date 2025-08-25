# 🔧 Common Commands Reference

[🏠 Main](../README.md) > [📚 Documentation](README.md) > [🔧 Common Commands](COMMON_COMMANDS.md)

[← Back to Main Documentation](../README.md)

> **Centralized command reference for Works On My Machine**  
> Standard commands and workflows across all supported languages

## 📚 Documentation Navigation

**🏠 [Main Documentation](../README.md)**  
**📚 [Documentation Index](README.md)**  
**🔧 [Common Commands](COMMON_COMMANDS.md)** (You are here)  
**📋 [Documentation Rules](DOCUMENTATION_RULES.md)**  
**⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)**  
**🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)**

## Table of Contents
- [Quick Usage Commands](#-quick-usage-commands)
- [Language-Specific Commands](#-language-specific-commands)
- [Standard Workflows](#-standard-workflows)
- [Command Categories](#-command-categories)
- [Related Documentation](#-related-documentation)

## Related Documentation
- **🐍 [Python Development](languages/python/PYTHON.md)** - Python-specific commands and configuration
- **🟨 [JavaScript Development](languages/javascript/JAVASCRIPT.md)** - JavaScript-specific commands and configuration
- **📋 [Main README](../README.md)** - Project overview and installation
- **📚 [Documentation Rules](DOCUMENTATION_RULES.md)** - Documentation standards

## 🚀 Quick Usage Commands

### 🆕 **Project Creation**
```bash
# Create new projects
womm new python my-project
womm new javascript my-project
womm new detect my-project  # Auto-detect type

# Configure existing projects
womm new python --current-dir
womm new javascript --current-dir
```

### 🔍 **Linting and Quality**
```bash
# Language-specific linting
womm lint python
womm lint javascript
womm lint all  # All supported languages

# Automatic fixes
womm lint python --fix
womm lint javascript --fix
```

### ⚙️ **System Management**
```bash
# Installation
womm install
womm uninstall

# System detection and setup
womm system detect
womm system install python node git npm
```

### 📝 **Spell Checking**
```bash
# CSpell integration
womm spell install
womm spell setup project
womm spell check
```

## 📋 Language-Specific Commands

### 🐍 **Python Workflow**
```bash
# Development
make format         # Black + isort
make lint           # Ruff quality check
make test           # pytest
make test-cov       # Tests with coverage
make clean          # Cleanup

# Direct tools
black .
isort .
ruff check .
pytest
```

### 🟨 **JavaScript Workflow**
```bash
# Development
npm run dev         # Development server
npm run build       # Build project
npm run lint        # ESLint check
npm run lint:fix    # ESLint auto-fix
npm run format      # Prettier formatting
npm test            # Jest tests
npm run test:coverage # Tests with coverage

# Direct tools
eslint src/
prettier --write .
jest
```

## 🔄 Standard Workflows

### 🆕 **New Project Setup**
1. **Create project**: `womm new [language] [name]`
2. **Navigate**: `cd [name]`
3. **Install dependencies**: Language-specific install command
4. **Start development**: Language-specific dev command

### 🔒 **Pre-commit Workflow**
1. **Format code**: Language-specific format command
2. **Lint code**: Language-specific lint command
3. **Run tests**: Language-specific test command
4. **Commit**: `git add . && git commit -m "message"`

### 🔄 **Continuous Integration**
```bash
# Python CI
make lint && make test

# JavaScript CI
npm run lint && npm test

# Universal CI
womm lint all
```

## 🎯 Command Categories

### 🆕 **Project Management**
- `womm new` - Create new projects
- `womm install` - Install WOMM globally
- `womm uninstall` - Remove WOMM

### 🔍 **Quality Assurance**
- `womm lint` - Code quality checks
- `womm spell` - Spell checking
- Language-specific quality tools

### ⚙️ **System Tools**
- `womm system` - System detection and setup
- `womm deploy` - Deploy tools globally
- `womm context` - Windows context menu

### 📦 **Language Tools**
- Python: `make`, `black`, `isort`, `ruff`, `pytest`
- JavaScript: `npm run`, `eslint`, `prettier`, `jest`

---

**🔧 This reference centralizes common commands to avoid duplication across language-specific documentation.** 