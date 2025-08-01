# 🐍 Python Development Tools

> **Modern and complete Python development environment**  
> Black + isort + flake8 + pytest + pre-commit + VSCode

## 🚀 Quick Usage

```bash
# Create a new Python project
womm new python my-project

# In an existing project
cd my-existing-project
womm new python --current-dir

# Linting and formatting
womm lint python  # Auto-detection if in a Python project
womm lint python --fix  # Automatic formatting
```

## 📁 Python Tools Structure

```
languages/python/
├── 📋 PYTHON.md                 # This file
├── 📜 scripts/
│   ├── setup_project.py         # Python project initialization
│   └── lint.py                  # Complete linting
├── ⚙️ configs/
│   ├── .flake8                  # Linting configuration
│   └── .pre-commit-config.yaml  # Automatic hooks
├── 📝 templates/
│   ├── gitignore-python.txt     # Optimized .gitignore
│   ├── pyproject.toml.template  # Project template
│   ├── Makefile.template        # Make commands
│   └── DEVELOPMENT.md.template  # Development guide
└── 🔧 vscode/
    ├── settings.json            # VSCode configuration
    └── extensions.json          # Recommended extensions
```

## ⚙️ Included Configuration

### 🎨 **Formatting (Black + isort)**
- **Line length**: 88 characters
- **Automatic formatting** on save (VSCode)
- **Automatic import organization**
- **PEP 8 standards** respected

### 🔍 **Linting (flake8)**
- **Real-time quality checks**
- **Rules adapted** to modern tools
- **Smart exclusions** for tests and CLI
- **Metrics and statistics**

### 🧪 **Testing (pytest)**
- **Automatic test discovery**
- **Code coverage** included
- **Fixtures** and mocking supported
- **HTML reports** generated

### 🔒 **Pre-commit Hooks**
- **Automatic formatting** before commit
- **Mandatory quality checks**
- **Security** with bandit
- **General checks** (YAML, merge conflicts, etc.)

## 🛠️ Available Scripts

### 🆕 **Project Creation**
```bash
# Complete assistant
womm new python my-app

# Existing project configuration
womm new python --current-dir
```

### 🔧 **Development**
```bash
# Complete linting
womm lint python

# Automatic correction
womm lint python --fix

# Tests
pytest
```

### 📋 **Make (Linux/Mac)**
```bash
make help           # Complete help
make format         # Formatting (black + isort)
make lint           # Quality check
make test           # Unit tests
make test-cov       # Tests with coverage
make clean          # Cleanup
```

## 📦 Installed Dependencies

### 🎯 **Core Development**
- **black** - Automatic formatting
- **isort** - Import organization
- **flake8** - Linting and quality
- **pre-commit** - Git hooks

### 🧪 **Testing**
- **pytest** - Modern test framework
- **pytest-cov** - Code coverage
- **coverage** - Detailed metrics

### 🔍 **Quality Assurance**
- **bandit** - Security analysis
- **mypy** - Type checking (optional)

## 🎯 Provided Templates

### 📄 **pyproject.toml**
Modern configuration with:
- Project metadata
- Dev dependencies
- Tool configuration (black, isort, pytest)
- Entry scripts

### 📝 **.gitignore**
Complete exclusions:
- Python cache (`__pycache__`, `*.pyc`)
- Virtual environments
- Test and coverage tools
- Build and distribution
- IDEs and editors

### 🔧 **VSCode**
Automatic configuration:
- Format on save
- Real-time linting
- Test discovery
- Recommended extensions

## 💡 Recommended Workflow

### 1. **Initialization**
```bash
womm new python my-project
cd my-project
```

### 2. **Development**
- **VSCode** formats automatically
- **Pre-commit** checks before commit
- **Tests** continuously with pytest

### 3. **Before Commit**
```bash
make lint           # Verification
make test           # Tests
git add .
git commit -m "feat: new feature"  # Automatic hooks
```

## 🔧 Customization

### ⚙️ **Local Configuration**
Create a `.dev-tools.toml` file in your project:
```toml
[python]
line_length = 100      # Instead of 88
skip_flake8 = true     # Disable flake8
additional_deps = [    # Additional dependencies
    "fastapi",
    "pydantic"
]
```

### 🎨 **Personal VSCode**
VSCode settings can be overridden locally in the project's `.vscode/settings.json`.

## 🚨 Troubleshooting

### ❓ **Python Not Found**
```bash
# Check Python
python --version
which python

# Python 3 Alternative
python3 --version
```

### ❓ **Pre-commit Failure**
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Force pass
git commit --no-verify
```

### ❓ **Formatting Conflicts**
```bash
# Format manually
black .
isort .

# Then commit
git add -A && git commit
```

---

🐍 **Happy Python development!** For other languages, see the [📋 Main README](../../README.md)