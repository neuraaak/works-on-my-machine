# Project Creation

Complete guide to creating new projects with WOMM. Create Python, JavaScript, React, and Vue projects with modern development setup.

## Overview

WOMM provides comprehensive project creation for modern development workflows. Each project type comes with pre-configured development tools, testing setup, and best practices.

### Supported Project Types

- **Python** - Full Python development environment
- **JavaScript** - Node.js projects with modern tooling
- **React** - React applications with Vite
- **Vue** - Vue.js applications with Vite

## Quick Start

### Basic Project Creation

```bash
# Create Python project
womm new python my-python-app

# Create JavaScript project
womm new javascript my-js-app

# Create React project
womm new react my-react-app

# Create Vue project
womm new vue my-vue-app
```

### Interactive Mode

```bash
# Guided project creation
womm new --interactive
```

### Custom Configuration

```bash
# Create with custom author and target directory
womm new python my-app --target ./projects/ --author-name "John Doe" --author-email "john@example.com"
```

### Quick Interactive Creation

```bash
# Guided project creation
womm new --interactive
```

## Python Projects

### Python Syntax

```bash
womm new python [PROJECT_NAME] [OPTIONS]
```

### Python Options

- `PROJECT_NAME` - Name of the project (optional in interactive mode)
- `--current-dir` - Use current directory instead of creating new one
- `--target <PATH>` - Target directory for project creation
- `--interactive` - Run in interactive mode
- `--author-name <NAME>` - Author name
- `--author-email <EMAIL>` - Author email
- `--project-url <URL>` - Project URL
- `--project-repository <URL>` - Repository URL

### Python Examples

```bash
# Basic Python project
womm new python my-python-app

# Python project in specific directory
womm new python my-app --target ./python-projects/

# Python project with author info
womm new python my-app --author-name "John Doe" --author-email "john@example.com"

# Interactive Python project creation
womm new python --interactive
```

### Python Structure

```text
my-python-app/
├── pyproject.toml          # Project configuration
├── src/
│   └── my_python_app/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .gitignore
├── README.md
└── requirements.txt
```

## JavaScript Projects

### JavaScript Syntax

```bash
womm new javascript [PROJECT_NAME] [OPTIONS]
```

### JavaScript Options

- `PROJECT_NAME` - Name of the project
- `--target <PATH>` - Target directory
- `--interactive` - Interactive mode
- `--author-name <NAME>` - Author name
- `--author-email <EMAIL>` - Author email
- `--project-url <URL>` - Project URL
- `--project-repository <URL>` - Repository URL

### JavaScript Examples

```bash
# Basic JavaScript project
womm new javascript my-js-app

# JavaScript project with custom configuration
womm new javascript my-app --author-name "Jane Smith" --project-url "https://myapp.com"
```

### JavaScript Structure

```text
my-js-app/
├── package.json            # Node.js configuration
├── src/
│   └── index.js
├── tests/
│   └── index.test.js
├── .gitignore
├── README.md
└── .eslintrc.js
```

## React Projects

### React Syntax

```bash
womm new react [PROJECT_NAME] [OPTIONS]
```

### React Options

- `PROJECT_NAME` - Name of the React application
- `--target <PATH>` - Target directory
- `--interactive` - Interactive mode
- `--author-name <NAME>` - Author name
- `--author-email <EMAIL>` - Author email
- `--project-url <URL>` - Project URL
- `--project-repository <URL>` - Repository URL

### React Examples

```bash
# Basic React project
womm new react my-react-app

# React project with custom setup
womm new react my-app --target ./react-projects/ --author-name "John Doe"
```

### React Structure

```text
my-react-app/
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── index.html              # Entry point
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── components/
├── public/
├── .gitignore
└── README.md
```

## Vue Projects

### Vue Syntax

```bash
womm new vue [PROJECT_NAME] [OPTIONS]
```

### Vue Options

- `PROJECT_NAME` - Name of the Vue application
- `--target <PATH>` - Target directory
- `--interactive` - Interactive mode
- `--author-name <NAME>` - Author name
- `--author-email <EMAIL>` - Author email
- `--project-url <URL>` - Project URL
- `--project-repository <URL>` - Repository URL

### Vue Examples

```bash
# Basic Vue project
womm new vue my-vue-app

# Vue project with custom configuration
womm new vue my-app --author-name "Jane Smith" --project-url "https://myvueapp.com"
```

### Vue Structure

```text
my-vue-app/
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── index.html              # Entry point
├── src/
│   ├── App.vue
│   ├── main.js
│   └── components/
├── public/
├── .gitignore
└── README.md
```

## Interactive Mode

When using `--interactive`, WOMM guides you through:

1. **Project Type Selection** - Choose Python, JavaScript, React, or Vue
2. **Project Name** - Enter project name
3. **Target Directory** - Choose where to create the project
4. **Author Information** - Enter author name and email
5. **Project Details** - Enter project URL and repository
6. **Configuration** - Customize project settings

### Example Interactive Flow

```text
🎯 Select project type: [Python/JavaScript/React/Vue]
📝 Enter project name: my-awesome-app
📁 Enter target directory (or press Enter for current): ./projects/
👤 Enter author name: John Doe
📧 Enter author email: john@example.com
🌐 Enter project URL (optional): https://myapp.com
🔗 Enter repository URL (optional): https://github.com/john/my-app
```

## Best Practices

### Project Naming

- Use descriptive, lowercase names
- Separate words with hyphens or underscores
- Avoid special characters and spaces

### Directory Structure

- Keep source code in dedicated directories
- Separate tests from main code
- Use consistent naming conventions

### Configuration

- Set up proper author information
- Configure repository URLs early
- Use meaningful project descriptions

### Development Workflow

- Initialize git repository
- Set up proper .gitignore
- Configure development tools
- Write initial documentation

## Troubleshooting

### Permission Errors

```bash
# Check directory permissions
ls -la /target/directory

# Fix permissions if needed
chmod 755 /target/directory
```

### Project Name Conflicts

```bash
# Use different project name
womm new python my-app-v2

# Or specify different target directory
womm new python my-app --target ./different-location/
```

### Missing Dependencies

```bash
# Install WOMM dependencies
pip install works-on-my-machine

# Update WOMM
pip install --upgrade works-on-my-machine
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export WOMM_DEBUG=1

# Run project creation
womm new python my-app
```

## See Also

- [Getting Started](../getting-started.md) - Installation and first steps
- [CLI Reference](index.md) - Complete command documentation
- [Configuration Guide](../guides/configuration.md) - Advanced configuration
- [Examples](../examples/index.md) - Practical examples

---

This project creation guide provides everything you need to create modern, well-structured projects with WOMM.
