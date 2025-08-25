# 📝 Spell Check Guide

[🏠 Main](../../README.md) > [📚 Documentation](../README.md) > [🔧 CLI Documentation](README.md) > [📝 Spell Check](SPELL.md)

[← Back to CLI Documentation](README.md)

> **Complete guide to spell checking and dictionary management with WOMM**  
> Check spelling, manage dictionaries, and improve documentation quality

## 📚 Documentation Navigation

**🏠 [Main Documentation](../../README.md)**  
**📚 [Documentation Index](../README.md)**  
**🔧 [CLI Documentation](README.md)**  
**📝 [Spell Check](SPELL.md)** (You are here)  
**🔌 [API Documentation](../api/README.md)**

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [🔍 Spell Checking](#-spell-checking)
- [📚 Dictionary Management](#-dictionary-management)
- [🎨 Interactive Mode](#-interactive-mode)
- [🔧 Configuration](#-configuration)
- [💡 Best Practices](#-best-practices)
- [🔍 Troubleshooting](#-troubleshooting)

## 🎯 Overview

WOMM provides comprehensive spell checking capabilities for documentation, code comments, and text files. The system supports multiple languages and custom dictionaries.

### ✅ **Features**
- **Multi-language Support** - English, French, Spanish, German, etc.
- **Custom Dictionaries** - Project-specific terminology
- **Code Comments** - Spell check in code documentation
- **Documentation Files** - Markdown, text, and other formats

### 🔄 **Spell Check Workflow**
```
File Selection → Language Detection → Dictionary Loading → Spell Check → Issue Reporting → Correction
```

## 🚀 Quick Start

### **Basic Spell Check**
```bash
# Check current directory
womm spell

# Check specific file
womm spell README.md

# Check specific directory
womm spell --path ./docs/
```

### **Language-Specific Check**
```bash
# Check with specific language
womm spell --language en

# Check with French
womm spell --language fr

# Auto-detect language
womm spell --auto-detect
```

### **Advanced Options**
```bash
# Check with custom dictionary
womm spell --dictionary ./custom.dict

# Interactive spell check
womm spell --interactive

# Generate report
womm spell --report
```

## 🔍 Spell Checking

### **Command Syntax**
```bash
womm spell [OPTIONS] [FILES...]
```

### **Options**
- `--language <LANG>` - Specify language (en, fr, es, de, etc.)
- `--dictionary <PATH>` - Custom dictionary file
- `--interactive` - Interactive mode
- `--report` - Generate spell check report
- `--auto-fix` - Auto-fix common issues
- `--ignore-case` - Ignore case sensitivity

### **Supported Languages**
- **English** (en) - Default language
- **French** (fr) - Français
- **Spanish** (es) - Español
- **German** (de) - Deutsch
- **Italian** (it) - Italiano
- **Portuguese** (pt) - Português

### **Examples**
```bash
# Basic spell check
womm spell

# Check specific files
womm spell README.md docs/guide.md

# Check with French language
womm spell --language fr

# Interactive spell check
womm spell --interactive

# Generate HTML report
womm spell --report --format html
```

### **Spell Check Output**
```
📝 Spell Check Results
├── Files checked: 15
├── Words checked: 1,247
├── Errors found: 8
├── Suggestions: 12
└── Language: English (en)

❌ Errors found:
  • "recieve" → "receive" (line 23)
  • "occured" → "occurred" (line 45)
  • "seperate" → "separate" (line 67)

✅ Spell check completed
⚠️ 8 errors found, 12 suggestions available
```

## 📚 Dictionary Management

### **Custom Dictionaries**
```bash
# Create custom dictionary
womm spell dict create my-project.dict

# Add words to dictionary
womm spell dict add my-project.dict "WOMM" "CLI" "API"

# Remove words from dictionary
womm spell dict remove my-project.dict "oldword"

# List dictionary words
womm spell dict list my-project.dict
```

### **Dictionary Formats**
```bash
# Plain text format
WOMM
CLI
API
development
toolchain

# JSON format
{
  "words": ["WOMM", "CLI", "API"],
  "language": "en",
  "description": "Project-specific terms"
}
```

### **Dictionary Management Commands**
```bash
# Create dictionary
womm spell dict create [DICT_NAME]

# Add words
womm spell dict add [DICT_NAME] [WORDS...]

# Remove words
womm spell dict remove [DICT_NAME] [WORDS...]

# List words
womm spell dict list [DICT_NAME]

# Export dictionary
womm spell dict export [DICT_NAME] --format json

# Import dictionary
womm spell dict import [DICT_NAME] --file words.txt
```

### **Project Dictionaries**
```bash
# Create project dictionary
womm spell dict create .womm-spell.dict

# Add project terms
womm spell dict add .womm-spell.dict "WOMM" "CLI" "API" "template"

# Use project dictionary
womm spell --dictionary .womm-spell.dict
```

## 🎨 Interactive Mode

### **Interactive Spell Check**
When using `--interactive`, WOMM guides you through:

1. **File Selection** - Choose files to check
2. **Language Selection** - Select or auto-detect language
3. **Error Review** - Review each spelling error
4. **Correction** - Choose correction or ignore
5. **Dictionary Update** - Add words to dictionary

### **Interactive Commands**
```
📝 Interactive Spell Check
❌ "recieve" → "receive" (line 23, README.md)

Options:
  [1] Replace with "receive"
  [2] Replace with "receiver"
  [3] Ignore this error
  [4] Add to dictionary
  [5] Skip to next error

Enter choice (1-5): 1
```

### **Batch Operations**
```bash
# Auto-fix common errors
womm spell --auto-fix

# Ignore specific patterns
womm spell --ignore "*.py" --ignore "node_modules/*"

# Check only specific file types
womm spell --include "*.md" --include "*.txt"
```

## 🔧 Configuration

### **Spell Check Configuration**
```yaml
# .womm-spell.yml
spell_check:
  language: en
  dictionary: .womm-spell.dict
  ignore_patterns:
    - "*.py"
    - "node_modules/*"
    - ".git/*"
  include_patterns:
    - "*.md"
    - "*.txt"
    - "*.rst"
  auto_fix: true
  interactive: false
```

### **Global Configuration**
```bash
# Set default language
womm spell config --set language en

# Set default dictionary
womm spell config --set dictionary ~/.womm/default.dict

# Configure ignore patterns
womm spell config --set ignore-patterns "*.py,node_modules/*"
```

### **Project Configuration**
```bash
# Create project config
womm spell config --project

# Set project language
womm spell config --set language fr

# Add project-specific settings
womm spell config --set project-terms "WOMM,CLI,API"
```

## 💡 Best Practices

### **Dictionary Management**
- **Project Dictionaries** - Create dictionaries for each project
- **Team Sharing** - Share dictionaries across team members
- **Version Control** - Include dictionaries in version control
- **Regular Updates** - Update dictionaries with new terminology

### **Spell Check Workflow**
- **Pre-commit** - Run spell check before commits
- **CI/CD Integration** - Include in automated checks
- **Documentation Review** - Check all documentation files
- **Code Comments** - Include code comments in checks

### **Language Handling**
- **Multi-language Projects** - Use appropriate language for each file
- **Auto-detection** - Use language auto-detection when possible
- **Consistent Language** - Maintain consistent language within files
- **Translation Support** - Support for translated documentation

### **Error Handling**
- **False Positives** - Add technical terms to dictionaries
- **Context Awareness** - Consider context when correcting
- **User Review** - Always review auto-corrections
- **Learning** - Update dictionaries based on corrections

## 🔍 Troubleshooting

### **Common Issues**

**Dictionary not found:**
```bash
# Check dictionary path
womm spell dict list --path

# Create default dictionary
womm spell dict create default.dict

# Set dictionary path
womm spell config --set dictionary ./my-dict.dict
```

**Language not supported:**
```bash
# Check supported languages
womm spell --list-languages

# Install language support
womm spell --install-language fr

# Use custom dictionary
womm spell --dictionary custom-fr.dict
```

**Performance issues:**
```bash
# Optimize spell check
womm spell --optimize

# Use caching
womm spell --cache

# Limit file size
womm spell --max-file-size 1MB
```

### **Configuration Issues**

**Config not loaded:**
```bash
# Check config file
womm spell config --show

# Reset configuration
womm spell config --reset

# Create default config
womm spell config --init
```

**Pattern matching issues:**
```bash
# Validate patterns
womm spell config --validate-patterns

# Test patterns
womm spell --test-patterns "*.md"

# Debug pattern matching
womm spell --debug-patterns
```

### **File Issues**

**Encoding problems:**
```bash
# Check file encoding
womm spell --check-encoding

# Convert encoding
womm spell --convert-encoding utf-8

# Handle special characters
womm spell --handle-special-chars
```

**Large file handling:**
```bash
# Process large files
womm spell --chunk-size 1000

# Skip large files
womm spell --max-file-size 10MB

# Process in background
womm spell --background
```

### **Debug Mode**
Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export WOMM_DEBUG=1

# Run spell check with debug output
womm spell --debug

# Check logs
cat ~/.womm/logs/spell.log
```

### **Log Files**
WOMM creates detailed logs for troubleshooting:

```bash
# View spell check logs
cat ~/.womm/logs/spell.log

# View dictionary logs
cat ~/.womm/logs/dictionary.log

# View configuration logs
cat ~/.womm/logs/config.log
```

---

**📝 This spell check guide provides comprehensive instructions for improving documentation quality with automated spell checking and dictionary management.**
