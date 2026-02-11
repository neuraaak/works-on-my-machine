# Linting Guide

> **Complete guide to code quality and linting with WOMM**
> Improve code quality with automated linting, formatting, and analysis tools

## 🎯 Overview

WOMM provides comprehensive code quality tools for all supported languages. The linting system automatically detects project types and applies appropriate quality checks.

### ✅ **Supported Tools**

- **🐍 Python**: flake8, black, isort, mypy, pylint
- **🟨 JavaScript**: ESLint, Prettier, TypeScript
- **⚛️ React**: ESLint React rules, Prettier
- **💚 Vue**: ESLint Vue rules, Prettier

### 🔄 **Linting Workflow**

```text
Project Detection → Tool Selection → Code Analysis → Issue Reporting → Auto-fixing
```

## 🚀 Quick Start

### **Basic Linting**

```bash
# Lint current project
womm lint

# Lint specific project
womm lint --path ./my-project/

# Interactive linting
womm lint --interactive
```

### **Language-Specific Linting**

```bash
# Python linting
womm lint python

# JavaScript linting
womm lint javascript

# React linting
womm lint react

# Vue linting
womm lint vue
```

### **Advanced Options**

```bash
# Lint with auto-fix
womm lint --fix

# Lint with specific tools
womm lint --tools black,flake8

# Generate quality report
womm lint --report
```

## 🐍 Python Linting

### **Command Syntax**

```bash
womm lint python [OPTIONS]
```

### **Options**

- `--path <PATH>` - Python project directory
- `--interactive` - Interactive mode
- `--fix` - Auto-fix issues where possible
- `--tools <TOOLS>` - Specific linting tools
- `--report` - Generate quality report

### **Python Linting Tools**

- **flake8** - Style guide enforcement
- **black** - Code formatting
- **isort** - Import sorting
- **mypy** - Type checking
- **pylint** - Comprehensive analysis

### **Examples**

```bash
# Basic Python linting
womm lint python

# Python linting with auto-fix
womm lint python --fix

# Python linting with specific tools
womm lint python --tools black,flake8

# Interactive Python linting
womm lint python --interactive
```

### **Python Configuration**

```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503

# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
multi_line_output = 3
```

## 🟨 JavaScript Linting

### **Command Syntax - JavaScript**

```bash
womm lint javascript [OPTIONS]
```

### **Options - JavaScript**

- `--path <PATH>` - JavaScript project directory
- `--interactive` - Interactive mode
- `--fix` - Auto-fix issues
- `--tools <TOOLS>` - Specific linting tools
- `--report` - Generate quality report

### **JavaScript Linting Tools**

- **ESLint** - JavaScript linting
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **Stylelint** - CSS/SCSS linting

### **Examples - JavaScript**

```bash
# Basic JavaScript linting
womm lint javascript

# JavaScript linting with auto-fix
womm lint javascript --fix

# JavaScript linting with specific tools
womm lint javascript --tools eslint,prettier

# Interactive JavaScript linting
womm lint javascript --interactive
```

### **JavaScript Configuration**

```json
// .eslintrc.js
module.exports = {
  extends: ['eslint:recommended'],
  rules: {
    'no-unused-vars': 'error',
    'no-console': 'warn'
  }
};

// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2
}
```

## ⚛️ React Linting

### **Command Syntax - React**

```bash
womm lint react [OPTIONS]
```

### **Options - React**

- `--path <PATH>` - React project directory
- `--interactive` - Interactive mode
- `--fix` - Auto-fix issues
- `--tools <TOOLS>` - Specific linting tools
- `--report` - Generate quality report

### **React Linting Tools**

- **ESLint React** - React-specific rules
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **React Testing Library** - Testing best practices

### **Examples - React**

```bash
# Basic React linting
womm lint react

# React linting with auto-fix
womm lint react --fix

# React linting with specific tools
womm lint react --tools eslint,prettier

# Interactive React linting
womm lint react --interactive
```

### **React Configuration**

```json
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended'
  ],
  plugins: ['react', 'react-hooks'],
  rules: {
    'react/prop-types': 'warn',
    'react-hooks/rules-of-hooks': 'error'
  }
};
```

## 💚 Vue Linting

### **Command Syntax - Vue**

```bash
womm lint vue [OPTIONS]
```

### **Options - Vue**

- `--path <PATH>` - Vue project directory
- `--interactive` - Interactive mode
- `--fix` - Auto-fix issues
- `--tools <TOOLS>` - Specific linting tools
- `--report` - Generate quality report

### **Vue Linting Tools**

- **ESLint Vue** - Vue-specific rules
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **Vue Test Utils** - Testing best practices

### **Examples - Vue**

```bash
# Basic Vue linting
womm lint vue

# Vue linting with auto-fix
womm lint vue --fix

# Vue linting with specific tools
womm lint vue --tools eslint,prettier

# Interactive Vue linting
womm lint vue --interactive
```

### **Vue Configuration**

```json
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended'
  ],
  plugins: ['vue'],
  rules: {
    'vue/multi-word-component-names': 'warn',
    'vue/no-unused-vars': 'error'
  }
};
```

## 🎨 Interactive Mode

### **Interactive Linting Process**

When using `--interactive`, WOMM guides you through:

1. **Project Detection** - Auto-detect project type
2. **Tool Selection** - Choose linting tools
3. **Configuration** - Customize linting rules
4. **Analysis** - Run linting checks
5. **Issue Resolution** - Review and fix issues

### **Example Interactive Flow**

```text
🔍 Detected project type: python
🔧 Linting tools:
  ☑ flake8 (style guide)
  ☑ black (formatting)
  ☑ isort (imports)
  ☑ mypy (type checking)

📊 Analysis results:
  ⚠️  5 style issues found
  ✅ All type checks passed
  🔧 3 issues auto-fixed
```

## 🔧 Configuration

### **Global Configuration**

```bash
# Create global linting config
womm lint config --global

# Set default tools
womm lint config --set-default-tools python:flake8,black
```

### **Project-Specific Configuration**

```bash
# Create project config
womm lint config --project

# Customize rules
womm lint config --customize-rules
```

### **Configuration Files**

- **Python**: `.flake8`, `pyproject.toml`, `setup.cfg`
- **JavaScript**: `.eslintrc.js`, `.prettierrc`, `tsconfig.json`
- **React**: `.eslintrc.js`, `.prettierrc`, `tsconfig.json`
- **Vue**: `.eslintrc.js`, `.prettierrc`, `tsconfig.json`

## 📊 Quality Metrics

### **Code Quality Metrics**

- **Complexity** - Cyclomatic complexity analysis
- **Maintainability** - Code maintainability index
- **Test Coverage** - Test coverage percentage
- **Technical Debt** - Code quality debt assessment

### **Quality Reports**

```bash
# Generate comprehensive report
womm lint --report --output html

# Export metrics
womm lint --metrics --format json

# Track quality over time
womm lint --track --history
```

### **Quality Thresholds**

```yaml
# .womm-quality.yml
thresholds:
  complexity: 10
  maintainability: 65
  coverage: 80
  technical_debt: 5
```

## 💡 Best Practices

### **Linting Strategy**

- **Early Integration** - Run linting during development
- **Automated Checks** - Integrate with CI/CD pipelines
- **Gradual Adoption** - Start with basic rules
- **Team Consensus** - Agree on coding standards

### **Configuration Management**

- **Version Control** - Track configuration changes
- **Team Sharing** - Share configurations across team
- **Environment Specific** - Different rules for dev/prod
- **Documentation** - Document custom rules

### **Issue Resolution**

- **Priority Classification** - Categorize issues by severity
- **Auto-fixing** - Use auto-fix where possible
- **Manual Review** - Review complex issues manually
- **Continuous Improvement** - Regular rule updates

## 🔍 Troubleshooting

### **Common Issues**

**Tool installation errors:**

```bash
# Check tool availability
womm lint --check-tools

# Install missing tools
womm lint --install-tools

# Update tools
womm lint --update-tools
```

**Configuration conflicts:**

```bash
# Validate configuration
womm lint --validate-config

# Reset configuration
womm lint --reset-config

# Merge configurations
womm lint --merge-config
```

**Performance issues:**

```bash
# Optimize linting
womm lint --optimize

# Use caching
womm lint --cache

# Parallel processing
womm lint --parallel
```

### **Debug Mode**

Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export WOMM_DEBUG=1

# Run linting with debug output
womm lint python --path ./my-project/
```

### **Log Files**

WOMM creates detailed logs for troubleshooting:

```bash
# View linting logs
cat ~/.womm/logs/lint.log

# View error logs
cat ~/.womm/logs/lint-errors.log
```

---

**🔍 This linting guide provides comprehensive instructions for improving code quality with automated tools and best practices.**
