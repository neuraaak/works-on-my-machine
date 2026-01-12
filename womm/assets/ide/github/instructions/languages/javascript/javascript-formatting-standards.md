
# JavaScript/TypeScript Formatting Standards

Code formatting and comment standards that enable easy navigation and clear structure identification in JavaScript and TypeScript files. These standards prioritize readability and maintainability through consistent section markers and organized code layout.

## Overview

Consistent code formatting makes codebases easier to navigate, understand, and maintain. Well-structured files with clear section markers allow developers to quickly locate specific functionality and understand code organization at a glance.

The standards defined here focus on section markers, import organization, and documentation patterns that create visual landmarks in code files. This structure is particularly valuable in large codebases where quick navigation is essential.

## Section Markers

### Main Section Separators

Use forward slashes for main section separators to create clear visual boundaries between major code sections. This style provides excellent visibility and is easy to scan.

- **USE** `// ///////////////////////////////////////////////////////////////` for main section separators
- **PLACE** section title on the line immediately after the separator
- **USE** closing separator after section title for symmetry

```javascript
// ///////////////////////////////////////////////////////////////
// IMPORTS
// ///////////////////////////////////////////////////////////////
```

The forward slash separator creates a strong visual boundary that's easy to spot when scrolling through code. The symmetry of opening and closing separators helps define clear section boundaries.

### Subsection Markers

Use dashes for subsections within classes, functions, or modules to create hierarchy without overwhelming visual noise.

- **USE** `// ------------------------------------------------` for subsections within classes or functions
- **PLACE** subsection title between dashes
- **USE** for grouping related methods or functionality

```javascript
// ------------------------------------------------
// ENHANCED METHODS
// ------------------------------------------------
```

Dash separators provide visual grouping without the weight of main section separators. They're ideal for organizing methods within a class, related functions within a module, or grouping related exports.

### Section Identification Patterns

Use clear section titles that immediately communicate the section's purpose. Combine section markers with descriptive titles for maximum clarity.

- **USE** uppercase section titles for main sections: `// IMPORTS`, `// CONSTANTS`, `// CLASSES`, `// FUNCTIONS`
- **USE** descriptive titles that match the section content
- **USE** `// ==> SECTION` pattern for special emphasis when needed

```javascript
// ==> CLASSES
// ///////////////////////////////////////////////////////////////
```

Clear section titles make it easy to jump to specific parts of a file using IDE navigation features. The `// ==>` pattern can be used for special emphasis on important sections.

## File Structure

### Standard File Layout

Organize files with a consistent structure that places related code together. This structure should be flexible enough to accommodate different file types (modules, classes, utilities) while maintaining consistency.

- **START** with file header comment describing the file's purpose (optional but recommended)
- **FOLLOW** with imports section
- **ORGANIZE** code into logical sections (constants, types/interfaces, classes, functions)
- **END** with exports if applicable

```javascript
// ///////////////////////////////////////////////////////////////
// MODULE_NAME - Brief Description
// Project: project_name
// ///////////////////////////////////////////////////////////////

/**
 * Module description.
 *
 * Detailed explanation of the module's purpose and functionality.
 */

// ///////////////////////////////////////////////////////////////
// IMPORTS
// ///////////////////////////////////////////////////////////////
// Standard library imports
import { readFile } from "fs/promises";
import { join } from "path";

// Third-party imports
import express from "express";
import { z } from "zod";

// Local imports
import { CustomError } from "./exceptions";
import { helperFunction } from "./utils";

// ///////////////////////////////////////////////////////////////
// TYPES & INTERFACES
// ///////////////////////////////////////////////////////////////
// Type definitions and interfaces

// ///////////////////////////////////////////////////////////////
// CONSTANTS
// ///////////////////////////////////////////////////////////////
// Configuration values and constants

// ///////////////////////////////////////////////////////////////
// CLASSES
// ///////////////////////////////////////////////////////////////
// Class definitions

// ///////////////////////////////////////////////////////////////
// FUNCTIONS
// ///////////////////////////////////////////////////////////////
// Function definitions

// ///////////////////////////////////////////////////////////////
// EXPORTS
// ///////////////////////////////////////////////////////////////
// Exported symbols

export { Class1, function1 };
```

This structure provides clear navigation points and makes it easy to understand file organization at a glance. The header comment with project name helps identify file context.

### Import Organization

Organize imports into logical groups with clear comments identifying each group. This makes dependencies obvious and helps identify import-related issues.

- **GROUP** imports into: standard library (Node.js built-ins), third-party, local
- **SEPARATE** groups with blank lines
- **USE** comments to identify each group
- **SORT** imports alphabetically within each group
- **PREFER** named imports over default imports when possible

```javascript
// ///////////////////////////////////////////////////////////////
// IMPORTS
// ///////////////////////////////////////////////////////////////
// Standard library imports (Node.js built-ins)
import { readFile, writeFile } from "fs/promises";
import { join, resolve } from "path";

// Third-party imports
import express from "express";
import { z } from "zod";
import type { Request, Response } from "express";

// Local imports
import { CustomError } from "../core/exceptions";
import { LoggingHandler } from "../core/interfaces";
import { helperFunction } from "./utils";
```

Clear import organization makes dependencies obvious and helps identify potential circular import issues. Grouping also makes it easier to see which external libraries a module depends on. Type-only imports should use `import type` in TypeScript.

## Class Structure

### Class Organization

Organize classes with clear section markers that identify different types of methods and properties. This makes it easy to navigate class implementations.

- **USE** `// ///////////////////////////////////////////////////////////////` for major class sections
- **USE** `// ------------------------------------------------` for method groups within classes
- **ORGANIZE** methods logically: constructor, properties, getters, setters, public methods, private methods
- **GROUP** related methods together with subsection markers

```javascript
class ExampleClass {
  // ///////////////////////////////////////////////////////////////
  // CONSTRUCTOR
  // ///////////////////////////////////////////////////////////////

  constructor(private param: string) {
    // Initialize the class
  }

  // ///////////////////////////////////////////////////////////////
  // PUBLIC METHODS
  // ///////////////////////////////////////////////////////////////

  publicMethod(): void {
    // Public method description
  }

  // ------------------------------------------------
  // PRIVATE METHODS
  // ------------------------------------------------

  private _privateMethod(): void {
    // Private method description
  }
}
```

Clear class organization makes it easy to find specific types of methods. The separation between public and private methods helps understand the class's API.

## Documentation Standards

### File Header Comments

File header comments should provide clear context about the file's purpose and functionality. Keep them concise but informative.

- **INCLUDE** brief description of file purpose
- **EXPLAIN** key functionality and use cases
- **MENTION** important dependencies or requirements
- **KEEP** header comments focused and readable

```javascript
// ///////////////////////////////////////////////////////////////
// UserService - User management service
// Project: my-app
// ///////////////////////////////////////////////////////////////
```

File header comments serve as the first point of reference for understanding a file's purpose. They should be informative without being verbose.

### JSDoc Comments

JSDoc comments provide type information and documentation for JavaScript/TypeScript code. Use JSDoc for functions, classes, and complex types.

- **USE** JSDoc for all public functions and methods
- **DOCUMENT** parameters with `@param` tags
- **DOCUMENT** return values with `@returns` tags
- **LIST** exceptions with `@throws` tags
- **INCLUDE** examples with `@example` tags for complex functions

```javascript
/**
 * Brief description of the function.
 *
 * Detailed explanation of what the function does, how it works,
 * and any important behavior or side effects.
 *
 * @param {string} param1 - Description of the first parameter
 * @param {number} [param2] - Description of the optional second parameter
 * @returns {boolean} Description of the return value
 * @throws {Error} When parameter validation fails
 *
 * @example
 * const result = exampleFunction('test', 42);
 * console.log(result); // true
 */
function exampleFunction(param1: string, param2?: number): boolean {
  // Implementation
}
```

JSDoc comments enable IDE tooltips and automatic documentation generation. They're particularly valuable for public APIs and complex functions.

### TypeScript Type Documentation

TypeScript provides type information through the type system, but complex types benefit from additional documentation.

- **DOCUMENT** complex type definitions with JSDoc
- **EXPLAIN** generic type parameters
- **DESCRIBE** discriminated unions and complex type patterns
- **INCLUDE** usage examples for complex types

```typescript
/**
 * Represents a user in the system.
 *
 * @template T - The type of additional user metadata
 */
interface User<T = Record<string, unknown>> {
  id: number;
  name: string;
  email: string;
  metadata: T;
}
```

Type documentation helps developers understand when and how to use complex types. It's especially valuable for generic types and discriminated unions.

## Inline Comments

### Comment Language

Comments should be written in English by default to maintain consistency across the codebase and enable international collaboration. Only use other languages when explicitly requested in a prompt or when working with code that has established non-English conventions.

- **WRITE** comments in English by default
- **USE** other languages only when explicitly mentioned in a prompt
- **MAINTAIN** language consistency within a file
- **PREFER** clear English over complex technical jargon

English comments ensure code is accessible to international teams and align with most JavaScript/TypeScript documentation standards. Consistency in comment language reduces cognitive load when reading code.

### Comment Guidelines

Inline comments should clarify non-obvious code behavior, not restate what the code does. Use comments to explain "why" rather than "what". Avoid comments that add no value or provide information that's already obvious from the code.

- **EXPLAIN** non-obvious behavior or design decisions
- **CLARIFY** complex logic or algorithms with high abstraction
- **DOCUMENT** workarounds, edge cases, or important gotchas
- **AVOID** comments that simply restate the code
- **AVOID** comments that add context-unrelated information
- **AVOID** comments that document obvious operations

```javascript
// Good: Explains why, not what
// Convert message to string safely - handles null and special objects
const message = safeStringConvert(value);

// Good: Documents complex abstraction
// Map log levels to patterns for consistent output formatting
const patternMap = {
  DEBUG: Pattern.DEBUG,
  INFO: Pattern.INFO,
};

// Bad: Restates what the code does
// Setting variable to 64
const x = 64;

// Bad: Adds unnecessary context
// This method is no longer legacy (removed in refactoring)
function processData(data: Array<Item>): void {
  // Implementation
}
```

Good comments explain the reasoning behind code, not just what it does. They're particularly valuable for complex logic, high abstraction levels, or non-obvious design decisions. Comments should add genuine value by explaining things that aren't immediately clear from reading the code.

### When to Comment

Comments should be used judiciously. Only add comments when they provide genuine value that cannot be inferred from the code itself.

- **COMMENT** complex sections with high abstraction or multiple layers of indirection
- **COMMENT** non-obvious behavior, edge cases, or gotchas that could surprise developers
- **COMMENT** workarounds, temporary solutions, or known limitations
- **COMMENT** business logic or domain-specific reasoning that isn't obvious from code
- **AVOID** commenting simple, self-explanatory code
- **AVOID** adding comments during refactoring that document the refactoring process itself
- **AVOID** comments that add meta-information about code changes or maintenance history

```javascript
// Good: Explains complex abstraction
// This decorator handles retry logic with exponential backoff, but
// skips retries for authentication errors to prevent account lockouts
@retryWithBackoff({ skipOn: [AuthenticationError] })
async function fetchUserData(userId: number): Promise<User> {
  // Implementation
}

// Good: Documents important gotcha
// Note: This function mutates the input array in-place for performance.
// Call array.slice() if you need to preserve the original.
function processItems(items: Array<Item>): void {
  // Implementation
}

// Bad: Obvious operation doesn't need comment
// Initialize the counter
let counter = 0;

// Bad: Meta-information about code changes
// Removed legacy code here, now using new implementation
function newMethod(): void {
  // Implementation
}
```

Comments are most valuable when they explain things that aren't obvious from the code: complex abstractions, non-obvious behavior, important edge cases, or domain-specific reasoning. Avoid comments that simply describe what the code does or add meta-information about code maintenance.

### Section Comments

Use section comments to group related code and provide context. These comments help organize code and make navigation easier.

- **USE** section comments to group related functionality
- **KEEP** section comments concise and descriptive
- **UPDATE** section comments when code structure changes

```javascript
// ------------------------------------------------
// ERROR HANDLING
// ------------------------------------------------

function handleError(error: Error): void {
  // Handle errors gracefully
}
```

Section comments create visual landmarks that make it easier to navigate code. They're especially useful in longer files.

## TypeScript-Specific Standards

### Type Annotations

TypeScript type annotations should be clear and helpful, not redundant. Let TypeScript infer types when they're obvious.

- **USE** explicit types for public APIs and function parameters
- **LET** TypeScript infer types for local variables when obvious
- **AVOID** redundant type annotations that don't add value
- **USE** `type` for unions and intersections, `interface` for object shapes

```typescript
// Good: Explicit types for public API
export function processUser(user: User): ProcessedUser {
  // Type is clear from parameter
  const processed = transformUser(user);
  return processed;
}

// Bad: Redundant type annotation
const count: number = items.length; // Type is obvious from assignment
```

Type annotations should add value by clarifying intent or enabling better type checking. Redundant annotations add noise without benefit.

### Interface vs Type Alias

Choose between `interface` and `type` based on their characteristics and use case.

- **USE** `interface` for object shapes that may be extended
- **USE** `type` for unions, intersections, and computed types
- **PREFER** `interface` for public APIs when both are applicable
- **USE** `type` for complex type transformations

```typescript
// Good: Interface for extensible object shape
interface User {
  id: number;
  name: string;
}

// Good: Type for union
type Status = "pending" | "completed" | "failed";

// Good: Type for complex transformation
type UserKeys = keyof User;
```

Interfaces are extendable and mergeable, making them ideal for public APIs. Type aliases are better for unions, intersections, and computed types.

## Best Practices

### Consistency

Consistency is more important than perfection. Choose a style and apply it consistently across the codebase.

- **MAINTAIN** consistent section marker style throughout the project
- **USE** the same import organization pattern in all files
- **FOLLOW** the same JSDoc format across modules
- **APPLY** formatting standards uniformly

Consistent formatting reduces cognitive load when reading code. Developers can focus on understanding logic rather than adapting to different formatting styles.

### Flexibility

These standards should be guidelines, not rigid rules. Adapt them to fit specific file needs while maintaining overall consistency.

- **ADAPT** structure to fit file-specific needs
- **OMIT** sections that don't apply to a particular file
- **ADD** sections when they improve organization
- **BALANCE** structure with readability

Over-structuring small files can reduce readability. Use structure where it adds value, not where it creates unnecessary overhead.

### Maintenance

Keep formatting standards up to date as the codebase evolves. Review and refine standards based on team feedback and changing needs.

- **REVIEW** formatting standards periodically
- **UPDATE** standards based on team feedback
- **DOCUMENT** any deviations or exceptions
- **ENFORCE** standards through code review and tooling (ESLint, Prettier)

Formatting standards should evolve with the codebase. Regular review ensures they remain useful and don't become outdated. Automated tooling helps enforce consistency without manual effort.
