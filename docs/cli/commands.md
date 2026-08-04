# 🔧 Common Commands Reference

> **Centralized command reference for Works On My Machine**  
> Standard commands and workflows across all supported languages

## Related Documentation {#related-documentation}

- **📋 [Main Documentation](../index.md)** - Project overview and installation

## 🚀 Quick Usage Commands {#quick-usage-commands}

### 🆕 **Project Creation**

```bash
# Create new projects from a catalog template
womm create official/python my-project
womm create official/javascript my-project

# Non-interactive, using template defaults
womm create official/python my-project --defaults --data project_name=my-project

# Configure an existing project (auto-detected type)
womm setup detect
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

## 📋 Language-Specific Commands {#language-specific-commands}

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

## 🔄 Standard Workflows {#standard-workflows}

### 🆕 **New Project Setup**

1. **Create project**: `womm create [template] [destination]`
2. **Navigate**: `cd [destination]`
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

## 🎯 Command Categories {#command-categories}

### 🆕 **Project Management**

- `womm create` - Create new projects from a Copier template
- `womm template` - Manage the Copier template catalog
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
