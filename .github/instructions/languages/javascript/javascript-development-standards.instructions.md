# JavaScript/TypeScript Development Standards & Optimization Rules

Professional JavaScript and TypeScript development practices focused on modern language features, type safety, and maintainable code patterns.

## JavaScript Ecosystem Foundations

### Package Management and Tooling

Modern package managers provide better performance, disk efficiency, and dependency resolution. Choose tools that support lock files and workspace management for monorepos.

- **USE** `pnpm` as primary package manager (faster, disk-efficient, strict dependency resolution)
- **IMPLEMENT** `package.json` with `"type": "module"` for ESM-first approach
- **USE** `npm` or `yarn` only when `pnpm` is unavailable
- **MAINTAIN** lockfile integrity with `pnpm-lock.yaml` in version control
- **IMPLEMENT** workspace monorepo with `pnpm-workspace.yaml` for complex projects
- **USE** `npx` for one-off tool execution, `pnpm dlx` for pnpm projects

Lock files ensure reproducible builds across environments. Workspace support enables efficient monorepo management with shared dependencies. ESM-first approach (`"type": "module"`) provides better tree-shaking and aligns with modern JavaScript standards.

### Modern JavaScript Features

ES2022+ introduces features that improve code quality, performance, and developer experience. Use these features when targeting supported environments.

- **USE** top-level `await` for module initialization
- **USE** private class fields (`#field`) and methods for encapsulation
- **PREFER** `async/await` over Promise chains for readability
- **USE** optional chaining (`?.`) and nullish coalescing (`??`) for safe property access
- **USE** template literals for string interpolation
- **USE** destructuring for object and array operations
- **USE** spread operator (`...`) for array/object operations

Private class fields provide true encapsulation without closures or WeakMaps. Optional chaining prevents verbose null checks. Nullish coalescing distinguishes between `null`/`undefined` and falsy values like `0` or `""`, which is often the desired behavior.

## TypeScript Excellence

### Type System Fundamentals

TypeScript's type system provides compile-time safety without runtime overhead. Use strict mode and leverage advanced type features to catch errors early.

- **USE** `strict: true` in `tsconfig.json` for maximum type safety
- **IMPLEMENT** `noImplicitAny: true` and `noImplicitReturns: true`
- **USE** `exactOptionalPropertyTypes: true` for precise optional handling
- **PREFER** `interface` for object shapes, `type` for unions/primitives
- **IMPLEMENT** exhaustive type checking with `never` type

Strict mode catches more errors at compile time, preventing runtime issues. Interfaces are extendable and mergeable, making them ideal for public APIs. Type aliases are better for unions, intersections, and computed types.

### Advanced Type Patterns

TypeScript's advanced type features enable sophisticated type-safe patterns. Use these features to create expressive, maintainable type definitions.

- **USE** `typing.Protocol`-like patterns with structural typing
- **USE** `Literal` types for string/numeric constants
- **IMPLEMENT** `TypedDict`-like patterns for structured objects
- **USE** generic constraints for type-safe abstractions
- **USE** conditional types and type inference for complex type transformations
- **USE** branded types for domain-specific primitives when needed
- **USE** template literal types for string-based APIs

Discriminated unions provide type-safe state machines. Template literal types enable type-safe string manipulation. Branded types prevent mixing semantically different primitives (like `UserId` and `ProductId` both being `number`).

## Code Quality Standards

### Formatting and Linting

Consistent code formatting and linting catch errors early and reduce cognitive load. Modern tools combine formatting and linting into fast, reliable solutions.

- **USE** `prettier` for code formatting with consistent configuration
- **USE** ESLint with TypeScript plugin for linting
- **CONFIGURE** ESLint flat config format (modern standard)
- **USE** `pre-commit` hooks to enforce formatting and linting
- **MAINTAIN** consistent configuration across team

ESLint flat config provides better performance and clearer configuration than legacy format. Pre-commit hooks catch issues before they reach version control, reducing friction in code reviews.

### Type Coverage and Documentation

TypeScript's type system improves code maintainability, but aim for pragmatic coverage rather than perfection. Focus on public APIs and critical paths.

- **IMPLEMENT** type hints for all public functions and methods
- **PRIORITIZE** critical paths and public APIs over internal helpers
- **USE** JSDoc comments for complex type relationships
- **INCLUDE** examples in JSDoc when they clarify usage
- **GENERATE** API documentation with TypeDoc or similar tools

Type coverage should be comprehensive but not obsessive. Internal helper functions can use inference when types are obvious. JSDoc complements TypeScript types by providing runtime documentation.

### Testing Practices

Test coverage is a means to an end, not an end in itself. Focus on testing critical business logic and edge cases rather than achieving arbitrary coverage percentages.

- **MAINTAIN** 80-90% test coverage with focus on critical business logic
- **USE** Vitest or Jest as the testing framework
- **USE** `describe` and `it` blocks for clear test organization
- **USE** `beforeEach` and `afterEach` for test setup and cleanup
- **IMPLEMENT** property-based testing with libraries when appropriate
- **USE** mocking libraries for external dependencies

Avoid testing implementation details. Focus on behavior and outcomes. Property-based testing is valuable for finding edge cases in complex logic. Mock external dependencies to ensure tests are fast and reliable.

## Performance Engineering

### Optimization Principles

Performance optimization should be data-driven, not speculative. Profile first to identify actual bottlenecks, then optimize only those code paths that matter.

- **PROFILE** before optimizing using browser DevTools or Node.js profilers
- **MEASURE** bundle size and load time in development
- **OPTIMIZE** only code paths that are actually bottlenecks
- **USE** lazy loading for code splitting
- **IMPLEMENT** memoization for expensive computations
- **USE** `requestAnimationFrame` for smooth animations

Premature optimization adds complexity without benefit. Bundle size directly impacts load time, especially on mobile networks. Code splitting reduces initial load time by loading code on demand.

### Bundle Optimization

Modern bundlers provide sophisticated optimization features. Configure them to minimize bundle size while maintaining code quality.

- **USE** tree-shaking to eliminate unused code
- **IMPLEMENT** code splitting for route-based or feature-based chunks
- **USE** dynamic imports for lazy loading
- **CONFIGURE** minification and compression
- **ANALYZE** bundle size regularly with bundle analyzers

Tree-shaking requires ESM modules and proper side-effect annotations. Code splitting reduces initial load time but increases the number of HTTP requests—balance these trade-offs. Dynamic imports enable lazy loading of routes, features, or heavy dependencies.

## Architectural Patterns

### Design Patterns

JavaScript's dynamic nature and rich ecosystem provide elegant ways to implement common design patterns. Choose patterns that fit JavaScript's philosophy.

- **USE** factory functions or classes with static methods for object creation
- **IMPLEMENT** repository pattern for data access abstraction
- **USE** observer pattern with EventEmitter or custom implementations
- **PREFER** composition over inheritance
- **USE** dependency injection for testability

Factory patterns provide clearer intent than complex constructors. Repository pattern abstracts data access, making it easier to swap implementations. Composition provides more flexibility than inheritance in JavaScript's prototype-based system.

### Module Organization

Well-organized modules improve maintainability and discoverability. Use clear module boundaries and consistent naming conventions.

- **ORGANIZE** code by feature or domain, not by file type
- **USE** index files for public API boundaries
- **EXPORT** only what's needed from modules
- **USE** barrel exports sparingly to avoid circular dependencies
- **MAINTAIN** consistent naming conventions across modules

Feature-based organization groups related code together, making it easier to understand and modify. Index files define clear module boundaries. Barrel exports can cause circular dependency issues and slow down IDE performance.

## Security and Production Hardening

### Security Best Practices

Security is not optional in production code. Follow established practices for input validation, XSS prevention, and secret management.

- **VALIDATE** all user inputs with strict schemas
- **SANITIZE** all dynamic content to prevent XSS
- **USE** Content Security Policy (CSP) headers
- **IMPLEMENT** proper CORS configuration
- **USE** HTTPS-only cookies with `httpOnly` and `secure` flags
- **STORE** all secrets in environment variables, never hardcode them
- **USE** `dotenv` for local development
- **USE** proper secret management systems for production

Input validation prevents injection attacks and data corruption. XSS prevention requires sanitizing all user-generated content. CSP headers provide defense-in-depth against XSS attacks. Environment variables prevent secrets from being committed to version control.

### Error Handling

Proper error handling makes debugging easier and provides better user experience. Create meaningful error hierarchies that reflect your domain model.

- **CREATE** custom error classes that extend `Error`
- **USE** specific error types for different error conditions
- **INCLUDE** context in error messages, but avoid exposing sensitive information
- **IMPLEMENT** error boundaries or global error handlers
- **USE** structured logging for error tracking

Custom error classes enable type-safe error handling. Specific error types allow callers to handle errors appropriately. Error boundaries prevent application crashes from propagating. Structured logging provides searchable, filterable error data.

## DevOps and Deployment

### Build Configuration

Modern build tools provide sophisticated optimization features. Configure them to balance build time, bundle size, and developer experience.

- **USE** modern build tools (Vite, esbuild, or similar)
- **CONFIGURE** source maps for production debugging
- **IMPLEMENT** environment-specific configurations
- **USE** path aliases for cleaner imports
- **CONFIGURE** proper chunk splitting strategies

Modern build tools provide faster builds and better developer experience than legacy tools. Source maps enable debugging production issues. Environment-specific configurations enable different behavior in development, staging, and production.

### Containerization

Docker containers provide consistent environments across development and production. Use best practices to minimize image size and ensure reliability.

- **USE** multi-stage Docker builds to minimize image size
- **SEPARATE** build dependencies from runtime dependencies
- **SPECIFY** exact Node.js version tags rather than using `latest`
- **INCLUDE** health checks in Dockerfiles
- **USE** `.dockerignore` to exclude unnecessary files

Multi-stage builds significantly reduce image size by excluding build tools from the final image. Health checks enable container orchestration systems to detect and restart unhealthy containers. `.dockerignore` prevents unnecessary files from being copied into the image.

## Code Generation Guidelines

### Modern JavaScript Syntax

Modern JavaScript syntax (ES2022+) provides more readable and expressive code. Use these features when targeting supported environments.

- **USE** `const` by default, `let` when reassignment is needed, avoid `var`
- **USE** arrow functions for concise function expressions
- **USE** template literals for string interpolation
- **USE** destructuring for object and array operations
- **USE** async/await for asynchronous operations
- **AVOID** mixing async and sync code unnecessarily

`const` prevents accidental reassignment and makes code intent clearer. Arrow functions provide concise syntax and lexical `this` binding. Template literals are more readable than string concatenation. Destructuring reduces boilerplate when working with objects and arrays.

### TypeScript Best Practices

TypeScript enhances JavaScript with type safety. Use TypeScript features effectively to catch errors early and improve code maintainability.

- **USE** type inference when types are obvious
- **AVOID** `any` type—use `unknown` when type is truly unknown
- **USE** type guards for runtime type checking
- **IMPLEMENT** function overloads for complex APIs
- **USE** utility types (`Partial`, `Pick`, `Omit`, etc.) for type transformations

Type inference reduces boilerplate when types are obvious. `unknown` is safer than `any` because it requires type checking before use. Type guards enable runtime type narrowing. Function overloads provide type-safe APIs for functions with multiple signatures.

## Continuous Integration

### Quality Gates

CI/CD pipelines should enforce quality standards without blocking development. Set reasonable thresholds that focus on critical issues rather than perfection.

- **CONFIGURE** CI/CD to run type checking, linting, and tests on every commit
- **USE** matrix builds to test against multiple Node.js versions
- **ENFORCE** 80-90% test coverage focused on critical paths
- **REQUIRE** all linting rules to pass
- **VALIDATE** TypeScript compilation with strict mode
- **SCAN** dependencies for vulnerabilities using `npm audit` or similar
- **CHECK** bundle size with bundle analyzers
- **USE** security pattern detection tools, but review findings carefully

Reasonable quality gates prevent technical debt without creating friction. False positives from security scanners are common, so review findings rather than blindly enforcing all rules. Bundle size limits should be pragmatic—monitor trends rather than enforcing strict limits.
