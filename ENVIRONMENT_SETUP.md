# 🛠️ Development Environment Manager

The Works On My Machine system includes an **automatic development environment manager** that automatically configures all necessary tools for your Python and JavaScript projects.

## 🎯 **Features**

### ✅ **Python - Complete Virtual Environment**
- **Automatic venv**: Virtual environment creation and configuration
- **Essential tools**: black, flake8, isort, pytest, pre-commit, mypy
- **Activation scripts**: `activate.bat` (Windows) and `activate.sh` (Unix)
- **Pre-commit hooks**: Automatic configuration

### ✅ **JavaScript - Complete npm Dependencies**
- **DevDependencies**: eslint, prettier, jest, husky
- **TypeScript support**: Auto-detection + TypeScript tools
- **Utility scripts**: `dev.bat` and `dev.sh` for quick start
- **Husky hooks**: Automatic configuration

### 🤔 **Smart Interactive Mode**
- **User prompt**: "Install development tools? (Y/n)"
- **Default installation**: Enter = Yes (smooth experience)
- **Detailed feedback**: Real-time progress and results

## 📋 **Usage**

### **Automatic Integration**
```bash
# When creating a project
new-python-project MyProject
# → Automatic prompt to install environment
# → Creates venv + installs all tools

new-js-project MyJSApp  
# → Automatic prompt to install environment
# → npm install + configures all tools
```

### **Dedicated Command**
```bash
# Manual configuration of existing project
setup-dev-env . python --no-prompt
setup-dev-env . javascript

# Test from any project
cd my-python-project
setup-dev-env . python
```

## 🐍 **Python Environment**

### **Automatically Installed Tools**
| Tool | Version | Description |
|------|---------|-------------|
| **black** | >=23.0.0 | Automatic code formatting |
| **flake8** | >=6.0.0 | Linting and style checking |
| **isort** | >=5.12.0 | Import organization |
| **pytest** | >=7.0.0 | Testing framework |
| **pytest-cov** | >=4.0.0 | Code coverage |
| **pre-commit** | >=3.0.0 | Automatic Git hooks |
| **mypy** | >=1.0.0 | Type checking |

### **Optional Tools (Bonus)**
- **bandit**: Security analysis
- **coverage**: Coverage reports
- **sphinx**: Documentation
- **wheel**: Build and distribution

### **Created Structure**
```
my-project/
├── venv/                 # Virtual environment
│   ├── Scripts/          # Windows
│   └── bin/              # Unix/Linux/macOS
├── activate.bat          # Windows activation script
├── activate.sh           # Unix activation script
├── src/
├── tests/
├── .flake8
├── pyproject.toml
└── .pre-commit-config.yaml
```

### **Python Workflow**
```bash
# 1. Create the project
new-python-project MyProject
# → "Install development tools? (Y/n): [Enter]"
# → ✅ venv created + tools installed

# 2. Activate environment
cd MyProject
activate.bat           # Windows
source activate.sh     # Unix

# 3. Develop
python src/my_module.py
pytest                 # Tests
black .                # Formatting
flake8                 # Linting
```

## 🟨 **JavaScript Environment**

### **Automatically Installed Tools**
| Tool | Description |
|------|-------------|
| **eslint** | JavaScript/TypeScript linting |
| **prettier** | Code formatting |
| **jest** | Testing framework |
| **husky** | Automatic Git hooks |
| **lint-staged** | Linting of modified files |

### **Automatic TypeScript Support**
If detected (tsconfig.json or TS dependency):
- **typescript**: TypeScript compiler
- **@typescript-eslint/parser**: ESLint parser for TS
- **@typescript-eslint/eslint-plugin**: ESLint TS rules
- **@types/node**: Node.js typings
- **ts-jest**: Jest for TypeScript
- **@types/jest**: Jest typings

### **Created Structure**
```
my-project/
├── node_modules/         # npm dependencies
├── dev.bat              # Windows development script
├── dev.sh               # Unix development script
├── src/
├── tests/
├── package.json
├── .eslintrc.json
├── prettier.config.js
└── .husky/              # Git hooks
    └── pre-commit
```

### **JavaScript Workflow**
```bash
# 1. Create the project
new-js-project MyJSApp
# → "Install development tools? (Y/n): [Enter]"
# → ✅ npm install + tools configured

# 2. Develop
cd MyJSApp
npm run dev            # Development server
npm test               # Tests
npm run lint           # Linting
npm run format         # Formatting
```

## ⚙️ **Advanced Configuration**

### **Smart Detection**
- **TypeScript**: Detects `tsconfig.json` or `typescript` dependency
- **Framework**: React, Vue, Node based on project type
- **Environment**: Adapts tools based on context

### **Generated Activation Scripts**

#### **Python - activate.bat (Windows)**
```batch
@echo off
echo 🐍 Activating Python environment for MyProject
call venv\Scripts\activate.bat
echo ✅ Environment activated - use 'deactivate' to exit
```

#### **JavaScript - dev.bat (Windows)**
```batch
@echo off
echo 🟨 Starting JavaScript environment for MyJSApp
echo 📦 Installing dependencies...
npm install
echo 🚀 Starting development server...
npm run dev
```

### **Automatic Pre-commit Configuration**
- **Python**: hooks for black, flake8, isort
- **JavaScript**: hooks for eslint, prettier

## 🎯 **Complete Workflow**

### **Scenario 1: New Python Project**
```bash
new-python-project MyAPI
```
```
🐍 Configuring Python environment for 'MyAPI'
📁 Directory: ./MyAPI

🛠️ Setting up development environment...
📦 Python tools to install:
  • Virtual environment (venv)
  • black (formatting)
  • flake8 (linting)
  • isort (import organization)
  • pytest (tests)
  • pre-commit (hooks)
  • mypy (type checking)

🤔 Install development tools? (Y/n): [Enter]
   📦 Creating virtual environment...
   📥 Installing essential tools...
   📥 Installing optional tools...
   ✓ Virtual environment created
   ✓ Python tools installed
   ✓ Pre-commit hooks configured
   ✓ Development environment configured

🎉 Development environment configured!
📁 Virtual environment: ./MyAPI/venv
🚀 Activation: activate.bat
🐍 Python: .\venv\Scripts\python.exe

🛠️ Installed tools:
  • black (formatting)
  • flake8 (linting)
  • isort (imports)
  • pytest (tests)
  • pre-commit (hooks)
  • mypy (types)

💡 Next steps:
  1. Activate environment: activate.bat
  2. Run tests: pytest
  3. Format code: black .
```

### **Scenario 2: JavaScript TypeScript Project**
```bash
new-js-project MyAppTS --type typescript
```
```
🟨 Configuring JavaScript environment for 'MyAppTS'
📁 Directory: ./MyAppTS

🛠️ Setting up development environment...
📦 JavaScript tools to install:
  • eslint (linting)
  • prettier (formatting)
  • typescript (if TypeScript)
  • jest (tests)
  • husky (hooks)

🤔 Install development tools? (Y/n): [Enter]
   📥 Installing development tools...
   📥 Installing test tools...
   📥 Installing hooks...
   ✓ JavaScript tools installed
   ✓ Husky configured
   ✓ Development environment configured

🎉 Development environment configured!
📁 Node modules: ./MyAppTS/node_modules
🚀 Development: npm run dev
🟨 Node.js: npm

🛠️ Installed tools:
  • eslint (linting)
  • prettier (formatting)
  • jest (tests)
  • husky (hooks)

💡 Next steps:
  1. Start the project: npm run dev
  2. Run tests: npm test
  3. Lint code: npm run lint
```

## 🔒 **Security and Automatic Exclusions**

### **Sensitive Files Protection**
The dev-tools include **automatic exclusions** to protect your sensitive data:

#### **Automatically Excluded Files**
- **Environment variables**: `.env*`, `.env.local`, `.env.*.local`
- **Secrets and keys**: `.secret*`, `*password*`, `*secret*`, `*.key`, `*.pem`, `*.crt`
- **Credentials directories**: `credentials/`, `keys/`

#### **Applied Exclusions**
✅ **VSCode**: Hidden from explorer and search  
✅ **Git**: Automatically in `.gitignore`  
✅ **CSpell**: Ignored by spell checking  
✅ **File watching**: No real-time monitoring  
✅ **Packaging scripts**: Excluded from distributions  

#### **Exclusions Example**
```
My-Project/
├── .env                    # ❌ Hidden
├── .env.local             # ❌ Hidden  
├── .secret                # ❌ Hidden
├── database_password.txt  # ❌ Hidden
├── server.key            # ❌ Hidden
├── credentials/           # ❌ Hidden directory
│   └── api_keys.json     # ❌ Hidden
├── src/                  # ✅ Visible
└── tests/                # ✅ Visible
```

### **Why It's Important**
1. **🛡️ Accidental protection**: Prevents secret commits
2. **⚡ Performance**: Reduces file watching
3. **🔍 Clean search**: Relevant results only
4. **📦 Secure distribution**: Packages without sensitive data

## 🚨 **Error Handling**

- **Python missing** → Offers to install via `dev-tools-install`
- **Node.js missing** → Offers to install via `dev-tools-install`
- **Insufficient permissions** → Clear instructions
- **Installation failure** → Suggests alternatives
- **Existing environment** → Detects and reuses

## 💡 **Benefits**

1. **🚀 Zero Configuration**: Everything works immediately after creation
2. **🎯 Isolated Environments**: No conflicts between projects
3. **📏 Modern Standards**: Current tools and practices
4. **🤝 Collaboration**: Same setup for the whole team
5. **⚡ Productive**: Focus on code, not configuration
6. **🔒 Secure**: Automatic protection of sensitive data

## 📈 **New Features & Improvements**

### **🔐 Enhanced Security (Recent)**
- **Automatic exclusions**: All sensitive files are hidden
- **Multi-level protection**: IDE, Git, CSpell, packaging
- **Smart detection**: Security patterns respected in all tools
- **Optimized performance**: Less monitoring on excluded files

### **🔍 Improved Project Detection**
- **Secure scanning**: Automatically ignores sensitive files
- **Contextual analysis**: Detection based on visible structure only
- **Preventive protection**: Avoids accidental indexing of secrets

---

**dev-tools transforms project creation into a smooth AND secure experience! 🎉🔒**