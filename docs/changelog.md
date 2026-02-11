# Changelog

All notable changes to this project are documented here.

This changelog is automatically generated from [Conventional Commits](https://www.conventionalcommits.org/).

## [3.0.0](https://github.com/neuraaak/works-on-my-machine/releases/tag/v3.0.0) — 2026-01-12

### Security

- Complete architectural refactoring with 4-layer standardized architecture ([d0ee5c3](https://github.com/neuraaak/works-on-my-machine/commit/d0ee5c36e4a3263bd73984b66a7dbf7a9da7aa73))

## [2.7.2](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.7.2) — 2026-01-06

### Features

- Update project structure and enhance build scripts ([208e95c](https://github.com/neuraaak/works-on-my-machine/commit/208e95c8193ff9719aa8bbbb8b09383eb17d29cf))

### Maintenance

- Bump version to 2.7.2 and enhance release workflow ([438e4b8](https://github.com/neuraaak/works-on-my-machine/commit/438e4b8ee61745703301c070bb7c08d79626837c))

## [2.7.0](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.7.0) — 2026-01-06

### Features

- Enhance project structure and add comprehensive exception handling ([5698f58](https://github.com/neuraaak/works-on-my-machine/commit/5698f586b5d10f57c9064e63666e37069532e5b9))

## [2.6.11](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.11) — 2025-08-28

### Bug Fixes

- Simplify execution messages and update push options in post-commit script ([2f8231c](https://github.com/neuraaak/works-on-my-machine/commit/2f8231c8c68616aedc2f2d01ed13398ac4149741))

## [2.6.10](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.10) — 2025-08-28

### Features

- Update version to 2.6.10 and improve execution messages ([4b8594d](https://github.com/neuraaak/works-on-my-machine/commit/4b8594d2ea10e80cbcbfe7e9d55cc1d8895efef5))

## [2.6.9](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.9) — 2025-08-28

### Features

- Bump version to 2.6.9 and enhance documentation ([b9baf27](https://github.com/neuraaak/works-on-my-machine/commit/b9baf27b62764fe715a86668ecee56d8ac09cba2))
- Ajout d'un workflow de publication automatisé avec un installeur exécutable et mise à jour du fichier .gitignore ([70c4a42](https://github.com/neuraaak/works-on-my-machine/commit/70c4a42a11462acb8ae95706f34e511f261e67cb))

## [2.6.8](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.8) — 2025-08-27

### Features

- V2.6.8 - Refactor exception handling and improve progress display ([cec93a0](https://github.com/neuraaak/works-on-my-machine/commit/cec93a0bbab2647494e5d7322b24f5e4d863d36c))

## [2.6.7](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.7) — 2025-08-27

### Features

- Add automated release workflow with executable installer ([f8c55a1](https://github.com/neuraaak/works-on-my-machine/commit/f8c55a123b9ae844fd424dbae237e1d9b8e77be3))

## [2.6.6](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.6) — 2025-08-26

### Features

- Refactor installation system to use pyproject.toml (v2.6.6) ([ba75336](https://github.com/neuraaak/works-on-my-machine/commit/ba75336f40c029e293763629d8c08d451635c07d))

## [2.6.5](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.5) — 2025-08-25

### Features

- **uninstall**: Harmonize uninstallation manager with installation patterns - v2.6.5 ([bd3e9e1](https://github.com/neuraaak/works-on-my-machine/commit/bd3e9e15d2973f1d38946fe418f026822433daac))

## [2.6.4](https://github.com/neuraaak/works-on-my-machine/releases/tag/v2.6.4) — 2025-08-25

### Features

- Major refactoring - v2.6.4 ([e0f830c](https://github.com/neuraaak/works-on-my-machine/commit/e0f830c0aa2fb71c5ba60fa5641b7abb2ac31856))

## [1.6.0](https://github.com/neuraaak/works-on-my-machine/releases/tag/v1.6.0) — 2025-08-03

### Features

- V1.6.0 - PyPI packaging configuration and installation exclusions ([bd2e298](https://github.com/neuraaak/works-on-my-machine/commit/bd2e298ee6211b9fac0e211b5577c2e0a4c6eef6))
- Refactor linting system to v1.4.0 - Centralize linting logic with LintManager and UI modules - Add structured results (LintResult, LintSummary) for better error handling - Implement consistent UI display with shared/ui/lint.py - Refactor womm/commands/lint.py as pure orchestrator - Support Python and WOMM project linting with ruff, black, isort, bandit - Add automatic tool availability checking and security exclusions - Provide detailed fix suggestions and progress reporting - Maintain backward compatibility with existing linting workflows ([2f9d615](https://github.com/neuraaak/works-on-my-machine/commit/2f9d6155903392e0032eca546aff428c8337c1c6))
- **security**: Comprehensive security improvements and code quality enhancements [v1.3.1] - Add SecurityValidator and SecureCLIManager for enhanced security - Resolve Ruff S604 warnings in cspell_manager.py with proper validation - Implement comprehensive test suite with pytest and coverage - Restructure project with modular architecture (core, security, tools, installation) - Add CSpell integration with French and technical dictionaries - Improve documentation with hierarchical navigation and English standards - Update pyproject.toml with modern tooling configuration (Black, isort, ruff, mypy) - Add pre-commit hooks and development workflow improvements - Implement proper error handling and logging throughout the codebase - Follow PEP 8 style guide and maintain type hints - Version bump to 1.3.1 for security and quality improvements ([52cbd77](https://github.com/neuraaak/works-on-my-machine/commit/52cbd77fd135ee8e58a40e11b5f0f5e07911ec8e))
- **cli**: Migrate to full Click CLI with 'womm' command and .womm directory ([02468a2](https://github.com/neuraaak/works-on-my-machine/commit/02468a286073e56081823a621e3f8faebed96ff0))
- **installer**: Add npm support to dev-tools-install ([443f626](https://github.com/neuraaak/works-on-my-machine/commit/443f6267372d1a803d86dba4e175ce4d5b550160))
- **cli**: Implement Click-based CLI architecture ([3c92bb3](https://github.com/neuraaak/works-on-my-machine/commit/3c92bb305e37f6eecee010bd4dc39ee02d238f2b))
- Release v1.0.0 - comprehensive multi-language development environment ([881fff1](https://github.com/neuraaak/works-on-my-machine/commit/881fff1d71f33a917c5a1471e661ccaaf9925b85))

### Bug Fixes

- **cli**: Migrate system_detector.py to use cli_manager ([088b38b](https://github.com/neuraaak/works-on-my-machine/commit/088b38bd5ed928542a8b1688832c860ec661570d))

### Refactoring

- Remove obsolete deploy command - Remove womm/commands/deploy.py (obsolete wrapper) - Remove shared/installation/deploy-devtools.py (referenced non-existent scripts) - Clean up imports and CLI registration - deploy functionality redundant with install command - Scripts referenced by deploy-devtools.py never existed (new-project.py, etc.) - Modern CLI architecture with womm command replaces global command deployment ([7e1fbac](https://github.com/neuraaak/works-on-my-machine/commit/7e1fbacd6a8981e4d4071a0906691dca34a2dde1))
- Major CLI architecture overhaul and documentation update ([65d0ea1](https://github.com/neuraaak/works-on-my-machine/commit/65d0ea1d99287f368bfbab8b04d9d566341a7ebb))
- **cli**: Improve wom.py formatting and imports ([3b73771](https://github.com/neuraaak/works-on-my-machine/commit/3b737710e0bc9addb6972d9760a47f30dde6fcbf))

### Documentation

- Update CLI manager docstring to English for consistency ([60811ee](https://github.com/neuraaak/works-on-my-machine/commit/60811eee947a2d141ec48c12e99586c38491ae76))

### V0.2.1

- Fix installation and executable issues - Fix womm.bat creation with correct relative path - Add ~/.womm to security validator allowed directories - Remove bin directory and wrapper scripts - Simplify installation process - Fix command execution from installed directory ([61f2587](https://github.com/neuraaak/works-on-my-machine/commit/61f2587312fd8b5a40469810fd06aeebef35bf58))

### V1.3.2

- Fix installation/uninstallation process and improve business logic architecture - Fix Windows PATH configuration with direct registry verification - Remove complex PATH counting logic and use simple reg query validation - Remove context menu management from uninstallation process - Improve installation verification by removing problematic executable tests - Fix Unicode encoding issues with subprocess.run and Rich UI - Simplify \_verify_installation to only check file existence - Add proper error handling and rollback mechanisms - Ensure consistent business logic pattern across install/uninstall commands - Clean up code architecture and remove deprecated functionality - Improve reliability and reduce installation failures ([aab22b1](https://github.com/neuraaak/works-on-my-machine/commit/aab22b174b11bb688dc86955929990727e2f88ef))

### V1.5.0

- Refactor spell command with improved CSpell detection and UI consistency ([f892b73](https://github.com/neuraaak/works-on-my-machine/commit/f892b73c0b1005fb41e4dd485718d0e401152bee))

---

_Automatically generated by [git-cliff](https://git-cliff.org/)_
