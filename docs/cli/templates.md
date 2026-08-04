# Template Management Guide

> **Complete guide to the WOMM Copier template catalog**
> List, inspect, register, update, and scaffold Copier templates

## 🎯 Overview

WOMM renders new projects with [Copier](https://copier.readthedocs.io/). The
`womm template` command manages the *catalog* of templates that `womm
create` can render from — it never renders a project itself (that's
`womm create`'s job, see [Project Creation](create.md)). The catalog CRUD
operations and the actual template rendering are deliberately separate
verticals.

### ✅ **Key Features**

- **Official Catalog** - `official/python` and `official/javascript` ship with WOMM
- **User Templates** - Register your own local Copier templates under the user namespace
- **Template Skeleton Scaffolding** - Generate a new Copier template from a meta-template
- **Rich UI** - Table and detail views for the catalog

## 🚀 Quick Start

### **1. List Available Templates**

```bash
womm template list
```

### **2. Inspect a Template**

```bash
womm template show official/python
```

### **3. Create a Project From a Template**

```bash
# Rendering itself is `womm create`, not `womm template`
womm create official/python ./my-project
```

### **4. Register Your Own Template**

```bash
womm template add my-template ./path/to/my-copier-template
```

## 📋 Template Commands

### **📋 `womm template list`**

List every known template (official catalog entries plus any user-registered
templates).

**Syntax:**

```bash
womm template list [-v]
```

### **ℹ️ `womm template show`**

Show a single catalog entry: its identifier, version, description and
source.

**Syntax:**

```bash
womm template show <IDENTIFIER>
```

**Example:**

```bash
womm template show official/python
```

### **➕ `womm template add`**

Register a local Copier template (a directory containing a `copier.yml`)
under the user namespace.

**Syntax:**

```bash
womm template add <IDENTIFIER> <SOURCE>
```

**Example:**

```bash
womm template add my-template ./path/to/my-copier-template
```

Remote sources (Git URLs) are not supported yet — only local directories.

### **➖ `womm template remove`**

Unregister a user template. Official catalog entries cannot be removed.

**Syntax:**

```bash
womm template remove <IDENTIFIER>
```

### **🔄 `womm template update`**

Point an existing user template at a new source directory.

**Syntax:**

```bash
womm template update <IDENTIFIER> <SOURCE>
```

### **🌱 `womm template init`**

Scaffold a brand-new Copier template skeleton (a `copier.yml` plus a
`template/` directory) — useful as a starting point before running
`womm template add` on the result.

**Syntax:**

```bash
womm template init <DESTINATION> [--data KEY=VALUE ...] [--defaults] [--force] [-v]
```

**Example:**

```bash
womm template init ./my-new-template --defaults --data template_name=my-new-template
```

## 📁 Template Storage

- **Official templates** ship inside the WOMM package itself (`official/python`, `official/javascript`).
- **User templates** registered with `womm template add` are recorded under `~/.womm/templates/` (or `%WOMM_HOME%` if set).

## 🔍 Troubleshooting

### **Template not found**

```bash
# Check available templates
womm template list

# Verify the identifier spelling
womm template show <identifier>
```

### **Debug Mode**

```bash
womm template list -v
```

## See Also

- [Project Creation](create.md) - Render a project from a catalog template with `womm create`
- [CLI Reference](index.md) - Complete command documentation

---

**📋 This template management guide covers the full `womm template` catalog surface: `list`, `show`, `add`, `remove`, `update`, `init`.**
