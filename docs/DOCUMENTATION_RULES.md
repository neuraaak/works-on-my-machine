# 📚 Documentation Rules & Standards

[🏠 Main](../README.md) > [📚 Documentation](README.md) > [📋 Documentation Rules](DOCUMENTATION_RULES.md)

[← Back to Main Documentation](../README.md)

> **Centralized documentation rules for Works On My Machine**  
> Ensuring consistency, relevance, and proper navigation across all documentation

## 📚 Documentation Navigation

**🏠 [Main Documentation](../README.md)**  
**📚 [Documentation Index](README.md)**  
**📋 [Documentation Rules](DOCUMENTATION_RULES.md)** (You are here)  
**🔧 [Common Commands](COMMON_COMMANDS.md)**  
**⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)**  
**🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)**

## Table of Contents
- [Documentation Principles](#-documentation-principles)
- [Document Structure Standards](#-document-structure-standards)
- [Link Standards](#-link-standards)
- [Content Guidelines](#-content-guidelines)
- [Formatting Standards](#-formatting-standards)
- [Maintenance Rules](#-maintenance-rules)
- [Quality Checklist](#-quality-checklist)
- [Related Documentation](#-related-documentation)

## Related Documentation
- **🔧 [Common Commands](COMMON_COMMANDS.md)** - Standard commands and workflows
- **📋 [Main README](../README.md)** - Project overview and installation
- **📚 [Documentation Index](README.md)** - Complete documentation hub

## 🎯 Documentation Principles

### 1. **English Language Standard**
- All documentation must be written in English
- Use clear, concise, and professional language
- Maintain consistent terminology across all files

### 2. **Documentation Directory Structure**
- All documentation must be placed in a `docs/` directory at the project root
- Mirror the project structure in the docs directory
- Example: `languages/python/` → `docs/languages/python/`
- Example: `shared/` → `docs/shared/`
- Example: `tests/` → `docs/tests/`
- Root-level documentation goes directly in `docs/`

### 3. **Hierarchical Navigation**
- Every document must include the navigation breadcrumb
- Use consistent link formatting: `[🏠 Main](../../README.md) > [🐍 Python](PYTHON.md)`
- Include "You are here" indicator for current page

### 4. **Information Relevance**
- Avoid duplication between documents
- Centralize common information in main README
- Language-specific docs focus only on language-specific content

## 📋 Document Structure Standards

### Required Sections for All Documents

```markdown
# 🐍 Document Title

[🏠 Main](../../README.md) > [🐍 Section](DOCUMENT.md)

[← Back to Main Documentation](../../README.md)

> **Brief description**  
> Key features and tools

## 📚 Documentation Navigation

**🏠 [Main Documentation](../../README.md)**  
**🐍 [Python Development](PYTHON.md)** (You are here)  
**🟨 [JavaScript Development](../javascript/JAVASCRIPT.md)**  
**⚙️ [Environment Setup](../../ENVIRONMENT_SETUP.md)**  
**🔧 [Prerequisites Installation](../../PREREQUISITE_INSTALLER.md)**

## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

## Related Documentation
- [Other Doc](../other/DOC.md) - Description
- [Main README](../../README.md) - Project overview
```

### Documentation Directory Structure
```
project-root/
├── docs/                           # All documentation
│   ├── README.md                   # Main documentation index
│   ├── COMMON_COMMANDS.md          # Centralized commands
│   ├── DOCUMENTATION_RULES.md      # This file
│   ├── ENVIRONMENT_SETUP.md        # Environment setup
│   ├── PREREQUISITE_INSTALLER.md   # Prerequisites
│   ├── languages/                  # Language-specific docs
│   │   ├── python/
│   │   │   └── PYTHON.md
│   │   └── javascript/
│   │       └── JAVASCRIPT.md
│   ├── shared/                     # Shared utilities docs
│   │   ├── CLI_ARCHITECTURE.md
│   │   └── system/
│   │       └── REGISTRATOR.md
│   └── tests/                      # Testing documentation
│       └── README.md
├── languages/                      # Actual code/tools
├── shared/                         # Actual shared code
└── tests/                          # Actual test code
```

### Navigation Breadcrumb Format
- **Main README**: `[🏠 Main](README.md)`
- **Language docs**: `[🏠 Main](../../README.md) > [🐍 Python](PYTHON.md)`
- **Sub-docs**: `[🏠 Main](../../../README.md) > [🐍 Python](../PYTHON.md) > [Sub](SUB.md)`

## 🔗 Link Standards

### Internal Links
- Use relative paths: `[Description](path/to/file.md)`
- Always include descriptive text in brackets
- Verify all links are functional

### Cross-References
- Link to related documentation in "Related Documentation" section
- Use consistent emoji indicators: 🏠 🐍 🟨 ⚙️ 🔧
- Include brief description of what each link provides

## 📝 Content Guidelines

### Information Hierarchy
1. **Main README**: Project overview, installation, global commands
2. **Language docs**: Language-specific tools, configuration, workflows
3. **Setup docs**: Environment and prerequisite installation
4. **Specialized docs**: Advanced topics, troubleshooting

### Content Relevance Rules
- **No duplication**: Information should appear in only one primary location
- **Cross-reference**: Use links instead of repeating information
- **Progressive disclosure**: Start with basics, link to details
- **Actionable content**: Focus on practical usage and examples

### Code Examples
- Use consistent formatting and syntax highlighting
- Include complete, runnable examples
- Provide both basic and advanced usage patterns
- Include expected outputs where helpful

## 🎨 Formatting Standards

### Headers
- Use emoji indicators consistently: 🚀 📚 🔧 🐍 🟨
- Maintain logical hierarchy (H1 > H2 > H3)
- Include anchor links in table of contents

### Code Blocks
- Use appropriate language tags: `bash`, `python`, `javascript`, `json`
- Include descriptive comments
- Format command examples clearly

### Lists and Tables
- Use consistent bullet points and numbering
- Include descriptive headers for tables
- Maintain alignment and readability

## 🔄 Maintenance Rules

### Regular Reviews
- Check all internal links monthly
- Verify code examples work with current versions
- Update version numbers and compatibility information
- Remove outdated or irrelevant content

### Update Process
1. Update content in primary location
2. Update cross-references if needed
3. Verify navigation links
4. Test all code examples
5. Update table of contents

## 📊 Quality Checklist

### Before Publishing
- [ ] All links are functional
- [ ] Navigation breadcrumbs are correct
- [ ] Code examples are tested
- [ ] No duplicate information exists
- [ ] Table of contents is complete
- [ ] Language is clear and professional
- [ ] Emoji usage is consistent
- [ ] Cross-references are accurate

### Content Validation
- [ ] Information is current and relevant
- [ ] Examples match actual functionality
- [ ] Troubleshooting covers common issues
- [ ] Installation steps are complete
- [ ] Configuration examples are accurate

---

**📚 These rules ensure consistent, maintainable, and user-friendly documentation across the entire project.** 