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

## 📋 Table of Contents
- [🎯 Documentation Principles](#-documentation-principles)
- [📁 Document Structure Standards](#-document-structure-standards)
- [🔗 Link Standards](#-link-standards)
- [📝 Content Guidelines](#-content-guidelines)
- [🎨 Formatting Standards](#-formatting-standards)
- [🔄 Maintenance Rules](#-maintenance-rules)
- [📊 Quality Checklist](#-quality-checklist)
- [🚀 Best Practices](#-best-practices)
- [⚠️ Common Pitfalls](#-common-pitfalls)
- [📚 Related Documentation](#-related-documentation)

## 📚 Related Documentation
- **🔧 [Common Commands](COMMON_COMMANDS.md)** - Standard commands and workflows
- **📋 [Main README](../README.md)** - Project overview and installation
- **📚 [Documentation Index](README.md)** - Complete documentation hub
- **⚙️ [Environment Setup](ENVIRONMENT_SETUP.md)** - Development environment configuration
- **🔧 [Prerequisites Installation](PREREQUISITE_INSTALLER.md)** - Required tools and dependencies

---

## 🎯 Documentation Principles

### 1. **English Language Standard**
- ✅ **All documentation MUST be written in English** - No exceptions
- ✅ Use clear, concise, and professional language
- ✅ Maintain consistent terminology across all files
- ✅ Avoid jargon and technical terms without explanation
- ✅ Use active voice when possible
- ✅ English is the mandatory language for all documentation files

### 2. **Documentation Directory Structure**
- ✅ All documentation must be placed in a `docs/` directory at the project root
- ✅ Mirror the project structure in the docs directory
- ✅ Example: `languages/python/` → `docs/languages/python/`
- ✅ Example: `shared/` → `docs/shared/`
- ✅ Example: `tests/` → `docs/tests/`
- ✅ Root-level documentation goes directly in `docs/`

### 3. **Hierarchical Navigation**
- ✅ Every document must include the navigation breadcrumb
- ✅ Use consistent link formatting: `[🏠 Main](../../README.md) > [🐍 Python](PYTHON.md)`
- ✅ Include "You are here" indicator for current page
- ✅ Maintain logical navigation flow

### 4. **Information Relevance**
- ✅ Avoid duplication between documents
- ✅ Centralize common information in main README
- ✅ Language-specific docs focus only on language-specific content
- ✅ Keep content focused and actionable

---

## 📁 Document Structure Standards

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

## 📋 Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

## 🎯 Overview
Brief introduction to the document's purpose and scope.

## 📝 Content Sections
Main content organized in logical sections.

## 🔗 Related Documentation
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
│   │   │   ├── PYTHON.md
│   │   │   ├── SETUP.md
│   │   │   └── TROUBLESHOOTING.md
│   │   └── javascript/
│   │       ├── JAVASCRIPT.md
│   │       ├── SETUP.md
│   │       └── TROUBLESHOOTING.md
│   ├── shared/                     # Shared utilities docs
│   │   ├── CLI_ARCHITECTURE.md
│   │   ├── SECURITY.md
│   │   └── system/
│   │       └── REGISTRATOR.md
│   └── tests/                      # Testing documentation
│       ├── README.md
│       ├── UNIT_TESTS.md
│       └── INTEGRATION_TESTS.md
├── languages/                      # Actual code/tools
├── shared/                         # Actual shared code
└── tests/                          # Actual test code
```

### Navigation Breadcrumb Format
- **Main README**: `[🏠 Main](README.md)`
- **Language docs**: `[🏠 Main](../../README.md) > [🐍 Python](PYTHON.md)`
- **Sub-docs**: `[🏠 Main](../../../README.md) > [🐍 Python](../PYTHON.md) > [Sub](SUB.md)`
- **Deep nested**: `[🏠 Main](../../../../README.md) > [🐍 Python](../../PYTHON.md) > [Sub](../SUB.md) > [Deep](DEEP.md)`

---

## 🔗 Link Standards

### Internal Links
- ✅ Use relative paths: `[Description](path/to/file.md)`
- ✅ Always include descriptive text in brackets
- ✅ Verify all links are functional
- ✅ Use anchor links for specific sections: `[Section](#section-name)`
- ✅ Test links after file moves or renames

### Cross-References
- ✅ Link to related documentation in "Related Documentation" section
- ✅ Use consistent emoji indicators: 🏠 🐍 🟨 ⚙️ 🔧 📚
- ✅ Include brief description of what each link provides
- ✅ Avoid circular references

### External Links
- ✅ Use HTTPS URLs when possible
- ✅ Include link descriptions for accessibility
- ✅ Verify external links periodically
- ✅ Consider link rot and update broken links

---

## 📝 Content Guidelines

### Information Hierarchy
1. **Main README**: Project overview, installation, global commands
2. **Language docs**: Language-specific tools, configuration, workflows
3. **Setup docs**: Environment and prerequisite installation
4. **Specialized docs**: Advanced topics, troubleshooting
5. **Reference docs**: API documentation, configuration options

### Content Relevance Rules
- ✅ **No duplication**: Information should appear in only one primary location
- ✅ **Cross-reference**: Use links instead of repeating information
- ✅ **Progressive disclosure**: Start with basics, link to details
- ✅ **Actionable content**: Focus on practical usage and examples
- ✅ **User-focused**: Write for the end user, not the developer

### Code Examples
- ✅ Use consistent formatting and syntax highlighting
- ✅ Include complete, runnable examples
- ✅ Provide both basic and advanced usage patterns
- ✅ Include expected outputs where helpful
- ✅ Add comments explaining complex logic
- ✅ Test all code examples before publishing

### Writing Style
- ✅ Use clear, concise sentences
- ✅ Write in present tense
- ✅ Use imperative mood for instructions
- ✅ Include step-by-step procedures
- ✅ Provide context for technical decisions

---

## 🎨 Formatting Standards

### Headers
- ✅ Use emoji indicators consistently: 🚀 📚 🔧 🐍 🟨 ⚙️ 🔗 📝
- ✅ Maintain logical hierarchy (H1 > H2 > H3 > H4)
- ✅ Include anchor links in table of contents
- ✅ Use descriptive header text
- ✅ Limit header depth to 4 levels maximum

### Code Blocks
- ✅ Use appropriate language tags: `bash`, `python`, `javascript`, `json`, `yaml`
- ✅ Include descriptive comments
- ✅ Format command examples clearly
- ✅ Use syntax highlighting for readability
- ✅ Include file paths for code examples

### Lists and Tables
- ✅ Use consistent bullet points and numbering
- ✅ Include descriptive headers for tables
- ✅ Maintain alignment and readability
- ✅ Use checkboxes for task lists: `- [ ] Task`
- ✅ Use numbered lists for sequential steps

### Emphasis and Highlighting
- ✅ Use **bold** for important terms and concepts
- ✅ Use *italic* for emphasis and foreign terms
- ✅ Use `code` for inline code, commands, and file names
- ✅ Use > blockquotes for notes and warnings
- ✅ Use consistent emphasis patterns

---

## 🔄 Maintenance Rules

### Regular Reviews
- ✅ Check all internal links monthly
- ✅ Verify code examples work with current versions
- ✅ Update version numbers and compatibility information
- ✅ Remove outdated or irrelevant content
- ✅ Review and update cross-references

### Update Process
1. ✅ Update content in primary location
2. ✅ Update cross-references if needed
3. ✅ Verify navigation links
4. ✅ Test all code examples
5. ✅ Update table of contents
6. ✅ Review for consistency and clarity

### Version Control
- ✅ Commit documentation changes with descriptive messages
- ✅ Include version numbers in commit messages
- ✅ Review documentation changes in pull requests
- ✅ Maintain documentation alongside code changes

---

## 📊 Quality Checklist

### Before Publishing
- [ ] All links are functional and tested
- [ ] Navigation breadcrumbs are correct
- [ ] Code examples are tested and working
- [ ] No duplicate information exists
- [ ] Table of contents is complete and accurate
- [ ] Language is clear and professional
- [ ] Emoji usage is consistent
- [ ] Cross-references are accurate
- [ ] File structure follows standards
- [ ] Content is up-to-date

### Content Validation
- [ ] Information is current and relevant
- [ ] Examples match actual functionality
- [ ] Troubleshooting covers common issues
- [ ] Installation steps are complete
- [ ] Configuration examples are accurate
- [ ] No broken links or references
- [ ] Grammar and spelling are correct
- [ ] Formatting is consistent

### Technical Validation
- [ ] Code examples compile/run successfully
- [ ] File paths are correct
- [ ] Version numbers are accurate
- [ ] Dependencies are listed correctly
- [ ] Configuration files are valid

---

## 🚀 Best Practices

### Documentation Planning
- ✅ Plan documentation structure before writing
- ✅ Identify target audience and their needs
- ✅ Create documentation outline
- ✅ Gather all necessary information
- ✅ Review existing documentation for gaps

### Writing Process
- ✅ Start with clear objectives
- ✅ Write in logical order
- ✅ Include practical examples
- ✅ Test all procedures
- ✅ Get feedback from users
- ✅ Iterate based on feedback

### Maintenance
- ✅ Schedule regular documentation reviews
- ✅ Keep documentation close to code
- ✅ Update documentation with code changes
- ✅ Monitor user feedback and questions
- ✅ Track documentation metrics

---

## ⚠️ Common Pitfalls

### Content Issues
- ❌ **Duplication**: Repeating information across multiple files
- ❌ **Outdated content**: Not updating documentation with code changes
- ❌ **Missing context**: Assuming reader knowledge
- ❌ **Incomplete examples**: Code that doesn't work as shown
- ❌ **Poor organization**: Unclear structure and navigation

### Technical Issues
- ❌ **Broken links**: Internal or external links that don't work
- ❌ **Inconsistent formatting**: Mixed styles and conventions
- ❌ **Missing files**: Referenced documentation that doesn't exist
- ❌ **Version mismatches**: Documentation not matching current code
- ❌ **Accessibility issues**: Poor structure for screen readers

### Process Issues
- ❌ **No review process**: Publishing without validation
- ❌ **Infrequent updates**: Documentation becoming stale
- ❌ **No user feedback**: Not incorporating user suggestions
- ❌ **Poor planning**: Writing without clear structure
- ❌ **Inconsistent standards**: Different rules for different docs

---

**📚 These rules ensure consistent, maintainable, and user-friendly documentation across the entire project.**

**🔄 Last updated**: [Current Date]  
**📋 Version**: 2.0  
**👥 Maintained by**: Documentation Team 