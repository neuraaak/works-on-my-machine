#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT CREATION SERVICE - JavaScript Project Creation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
JavaScript Project Creation Service - Singleton service for JavaScript project creation.

Handles JavaScript/Node.js/React/Vue project creation logic including:
- Project structure creation
- File generation from templates
- npm project initialization
- Dependency installation
- Development tools configuration
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import re
import shutil
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.project import (
    ProjectServiceError,
    TemplateServiceError,
)
from ...shared.results.project_results import ProjectCreationResult
from ...utils.common import get_assets_module_path
from ...utils.project import (
    check_npm_available,
    create_javascript_config_files,
    create_javascript_source_files,
    create_javascript_structure,
    install_npm_dependencies,
    install_npm_dev_dependencies,
    validate_project_name,
    validate_project_path,
    validate_project_type,
)
from ..common.command_runner_service import CommandRunnerService
from .template_service import TemplateService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT CREATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class JavaScriptProjectCreationService:
    """Singleton service for JavaScript project creation operations."""

    _instance: ClassVar[JavaScriptProjectCreationService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> JavaScriptProjectCreationService:
        """Create or return the singleton instance.

        Returns:
            JavaScriptProjectCreationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize JavaScript project creation service (only once)."""
        if JavaScriptProjectCreationService._initialized:
            return

        self._template_service = TemplateService()
        self._command_runner = CommandRunnerService()
        self._template_dir = (
            get_assets_module_path() / "languages" / "javascript" / "templates"
        )
        self.logger = logging.getLogger(__name__)
        JavaScriptProjectCreationService._initialized = True

    def create_project_structure(
        self, project_path: Path, project_name: str, project_type: str = "node"
    ) -> ProjectCreationResult:
        """Create the basic project structure.

        Args:
            project_path: Path where to create the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            ProjectCreationResult: Result with created directory information

        Raises:
            ProjectServiceError: If structure creation fails
            ProjectValidationError: If validation fails
        """
        try:
            created_dirs = create_javascript_structure(
                project_path, project_name, project_type
            )
            return ProjectCreationResult(
                success=True,
                message="Project structure created successfully",
                project_path=project_path,
                project_name=project_name,
                project_type=project_type,
                directories_created=(
                    created_dirs if isinstance(created_dirs, list) else []
                ),
            )

        except (ProjectServiceError, ValidationServiceError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_project_structure: {e}")
            raise ProjectServiceError(
                message=f"Failed to create project structure: {e}",
                operation="create_project_structure",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def create_project_files(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,
        **kwargs,
    ) -> ProjectCreationResult:
        """Create JavaScript-specific project files.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)
            **kwargs: Additional configuration options

        Returns:
            ProjectCreationResult: Result with created files information

        Raises:
            ProjectServiceError: If file creation fails
            TemplateError: If template processing fails
        """
        try:
            validate_project_path(project_path)
            validate_project_name(project_name)
            validate_project_type(project_type)

            created_files = []

            # Create package.json
            package_result = self._create_package_json(
                project_path, project_name, project_type, **kwargs
            )
            if package_result.success:
                created_files.append("package.json")

            # Create source files based on project type (always created)
            source_files = create_javascript_source_files(
                project_path, project_name, project_type
            )
            if isinstance(source_files, list):
                created_files.extend(source_files)

            # In minimal mode, skip dev config files
            minimal = kwargs.get("minimal", False)
            if not minimal:
                # Create configuration files
                config_files = create_javascript_config_files(project_path)
                if isinstance(config_files, list):
                    created_files.extend(config_files)

            return ProjectCreationResult(
                success=True,
                message="Project files created successfully",
                project_path=project_path,
                project_name=project_name,
                project_type=project_type,
                files_created=created_files,
            )

        except (
            ProjectServiceError,
            TemplateServiceError,
            ValidationServiceError,
        ):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_project_files: {e}")
            raise ProjectServiceError(
                message=f"Failed to create project files: {e}",
                operation="create_project_files",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def initialize_npm_project(
        self,
        project_path: Path,
        _project_name: str,
        **kwargs,  # noqa: ARG002
    ) -> ProjectCreationResult:
        """Initialize npm project.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            **kwargs: Additional configuration options

        Returns:
            ProjectCreationResult: Result of npm initialization

        Raises:
            ProjectServiceError: If npm project initialization fails
        """
        try:
            validate_project_path(project_path)

            # Check if npm is available
            if not check_npm_available():
                raise ProjectServiceError(
                    message="npm is not installed or not in PATH",
                    operation="initialize_npm_project",
                    details="npm command not found in PATH",
                )

            # package.json already created, so initialization is complete
            return ProjectCreationResult(
                success=True,
                message="npm project initialized successfully",
                project_path=project_path,
                project_name=_project_name,
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.error(f"initialize_npm_project failed: {e}")
            raise ProjectServiceError(
                message=f"Failed to initialize npm project: {e}",
                operation="initialize_npm_project",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_dependencies(
        self,
        project_path: Path,
        project_type: str,
    ) -> ProjectCreationResult:
        """Install project dependencies.

        Args:
            project_path: Path to the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            ProjectCreationResult: Result of dependency installation

        Raises:
            ProjectServiceError: If dependency installation fails
        """
        try:
            validate_project_path(project_path)
            validate_project_type(project_type)

            success = install_npm_dependencies(project_path)
            if not success:
                raise ProjectServiceError(
                    message="npm install command failed",
                    operation="install_dependencies",
                    details="npm install did not complete successfully",
                )

            return ProjectCreationResult(
                success=True,
                message="Dependencies installed successfully",
                project_path=project_path,
                project_type=project_type,
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.error(f"install_dependencies failed: {e}")
            raise ProjectServiceError(
                message=f"Failed to install dependencies: {e}",
                operation="install_dependencies",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_dev_tools(
        self, project_path: Path, project_type: str
    ) -> ProjectCreationResult:
        """Set up development tools.

        Args:
            project_path: Path to the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            ProjectCreationResult: Result of dev tools setup

        Raises:
            ProjectServiceError: If development tools setup fails
        """
        try:
            validate_project_type(project_type)

            # Check if npm is available
            if not shutil.which("npm"):
                raise ProjectServiceError(
                    message="npm is not installed or not in PATH",
                    operation="setup_dev_tools",
                    details="npm command not found in PATH",
                )

            # Install development dependencies
            dev_dependencies = [
                "eslint",
                "prettier",
                "husky",
                "lint-staged",
                "@types/node",
            ]

            # Add type-specific dev dependencies
            if project_type == "react":
                dev_dependencies.extend(
                    [
                        "@types/react",
                        "@types/react-dom",
                        "@testing-library/react",
                        "@testing-library/jest-dom",
                    ]
                )
            elif project_type == "vue":
                dev_dependencies.extend(
                    [
                        "@vue/cli-service",
                        "@vue/compiler-sfc",
                    ]
                )

            # Install dev dependencies
            success = install_npm_dev_dependencies(project_path, dev_dependencies)
            if not success:
                raise ProjectServiceError(
                    message="Failed to install development tools",
                    operation="setup_dev_tools",
                    details="npm install dev tools command failed",
                )

            return ProjectCreationResult(
                success=True,
                message="Development tools installed successfully",
                project_path=project_path,
                project_type=project_type,
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to set up development tools: {e}",
                operation="setup_dev_tools",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_git_repository(self, project_path: Path) -> ProjectCreationResult:
        """Initialize a Git repository for the project.

        Args:
            project_path: Path to the project

        Returns:
            ProjectCreationResult: Result of Git setup

        Raises:
            ProjectServiceError: If Git setup fails
        """
        try:
            # Check if git is available
            if not shutil.which("git"):
                logger.info("Git not found, skipping repository initialization")
                return ProjectCreationResult(
                    success=True,
                    message="Git repository setup skipped (git not found)",
                    project_path=project_path,
                    warnings=["Git not found in system PATH"],
                )

            # Initialize git repository using CommandRunnerService
            git_path = shutil.which("git")
            result = self._command_runner.run(
                [git_path, "init"],
                description="Initialize Git repository",
                cwd=project_path,
            )

            if result.returncode == 0:
                return ProjectCreationResult(
                    success=True,
                    message="Git repository initialized successfully",
                    project_path=project_path,
                )
            else:
                logger.warning(f"Failed to initialize Git repository: {result.stderr}")
                return ProjectCreationResult(
                    success=False,
                    message="Failed to initialize Git repository",
                    project_path=project_path,
                    error=result.stderr,
                )

        except ProjectServiceError:
            raise
        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to setup Git repository: {e}",
                operation="setup_git_repository",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_git_hooks(self, project_path: Path) -> ProjectCreationResult:
        """Set up Git hooks with Husky.

        Args:
            project_path: Path to the project

        Returns:
            ProjectCreationResult: Result of Git hooks setup

        Raises:
            ProjectServiceError: If Git hooks setup fails
        """
        try:
            # Initialize husky using CommandRunnerService
            npx_path = shutil.which("npx")
            result = self._command_runner.run(
                [npx_path, "husky", "install"],
                description="Install Husky Git hooks",
                cwd=project_path,
            )

            if result.returncode == 0:
                try:
                    # Add pre-commit hook using CommandRunnerService
                    npx_path = shutil.which("npx")
                    self._command_runner.run(
                        [
                            npx_path,
                            "husky",
                            "add",
                            ".husky/pre-commit",
                            "npm run lint-staged",
                        ],
                        description="Add pre-commit hook",
                        cwd=project_path,
                    )
                except Exception as e:
                    logger.warning(f"Failed to add pre-commit hook: {e}")
                return ProjectCreationResult(
                    success=True,
                    message="Git hooks installed successfully",
                    project_path=project_path,
                )
            else:
                logger.warning("Failed to initialize husky, but continuing")
                return ProjectCreationResult(
                    success=True,
                    message="Git hooks setup skipped",
                    project_path=project_path,
                    warnings=["Husky initialization failed"],
                )

        except ProjectServiceError:
            raise
        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to set up Git hooks: {e}",
                operation="setup_git_hooks",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _create_package_json(
        self, project_path: Path, project_name: str, project_type: str, **kwargs
    ) -> dict[str, Any]:
        """Create package.json configuration file.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)
            **kwargs: Additional configuration options

        Returns:
            dict: Metadata about file creation with 'success' key

        Raises:
            ProjectServiceError: If package.json creation fails
            TemplateError: If template processing fails
        """
        try:
            template_path = self._template_dir / "package.template.json"
            output_path = project_path / "package.json"

            # Base template variables
            template_vars = {
                "PROJECT_NAME": project_name,
                "PROJECT_DESCRIPTION": f"{project_name} - A JavaScript project created with WOMM CLI",
                "AUTHOR_NAME": kwargs.get("author_name", "Your Name"),
                "AUTHOR_EMAIL": kwargs.get("author_email", "your.email@example.com"),
                "PROJECT_URL": kwargs.get("project_url", ""),
                "PROJECT_REPOSITORY": kwargs.get("project_repository", ""),
                "PROJECT_DOCS_URL": kwargs.get("project_docs_url", ""),
                "PROJECT_KEYWORDS": kwargs.get(
                    "project_keywords", "javascript,node,cli"
                ),
                "MAIN_FILE": "src/main.js",
                "MODULE_TYPE": "commonjs",
                "DEV_COMMAND": "node src/main.js",
                "BUILD_COMMAND": "echo 'No build step required'",
                "START_COMMAND": "node src/main.js",
                "KEYWORDS": "javascript,node,cli",
                "JEST_ENVIRONMENT": "node",
                "DEPENDENCIES": "",
                "DEV_DEPENDENCIES": "",
                "PREPARE_SCRIPT": "",
            }

            # Add project type specific variables
            if project_type == "react":
                template_vars.update(
                    {
                        "PROJECT_TYPE": "react",
                        "FRAMEWORK_NAME": "React",
                        "FRAMEWORK_VERSION": "^18.2.0",
                        "MAIN_FILE": "src/index.jsx",
                        "MODULE_TYPE": "module",
                        "DEV_COMMAND": "react-scripts start",
                        "BUILD_COMMAND": "react-scripts build",
                        "START_COMMAND": "react-scripts start",
                        "KEYWORDS": "react,javascript,frontend",
                        "JEST_ENVIRONMENT": "jsdom",
                        "DEPENDENCIES": '"react": "^18.2.0",\n    "react-dom": "^18.2.0"',
                        "DEV_DEPENDENCIES": '"react-scripts": "^5.0.1",\n    "@testing-library/react": "^13.4.0",\n    "@testing-library/jest-dom": "^5.16.5"',
                    }
                )
            elif project_type == "vue":
                template_vars.update(
                    {
                        "PROJECT_TYPE": "vue",
                        "FRAMEWORK_NAME": "Vue",
                        "FRAMEWORK_VERSION": "^3.3.0",
                        "MAIN_FILE": "src/main.js",
                        "MODULE_TYPE": "module",
                        "DEV_COMMAND": "vue-cli-service serve",
                        "BUILD_COMMAND": "vue-cli-service build",
                        "START_COMMAND": "vue-cli-service serve",
                        "KEYWORDS": "vue,javascript,frontend",
                        "JEST_ENVIRONMENT": "jsdom",
                        "DEPENDENCIES": '"vue": "^3.3.0"',
                        "DEV_DEPENDENCIES": '"@vue/cli-service": "^5.0.0",\n    "@vue/compiler-sfc": "^3.3.0"',
                    }
                )
            else:  # node
                template_vars.update(
                    {
                        "PROJECT_TYPE": "node",
                        "FRAMEWORK_NAME": "Node.js",
                        "FRAMEWORK_VERSION": "^18.0.0",
                        "MAIN_FILE": "src/main.js",
                        "MODULE_TYPE": "commonjs",
                        "DEV_COMMAND": "node src/main.js",
                        "BUILD_COMMAND": "echo 'No build step required'",
                        "START_COMMAND": "node src/main.js",
                        "KEYWORDS": "javascript,node,cli",
                        "JEST_ENVIRONMENT": "node",
                        "DEPENDENCIES": "",
                        "DEV_DEPENDENCIES": "",
                    }
                )

            # Generate the package.json content
            self._template_service.generate_template(
                template_path, output_path, template_vars
            )

            # Fix JSON formatting issues
            try:
                with open(output_path, encoding="utf-8") as f:
                    json_content = f.read()

                # Remove trailing commas in devDependencies
                json_content = re.sub(r",\s*\n\s*},", "\n  },", json_content)

                # Fix empty dependencies sections
                json_content = json_content.replace(
                    '"dependencies": {\n    \n  },', '"dependencies": {},'
                )
                json_content = json_content.replace(
                    '"devDependencies": {\n    \n  },', '"devDependencies": {},'
                )

                # Remove empty DEV_DEPENDENCIES placeholder
                json_content = re.sub(r",\s*{{DEV_DEPENDENCIES}}", "", json_content)

                # Write the fixed content back
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_content)

            except Exception as e:
                logger.warning(f"Failed to fix JSON formatting: {e}")

            return {"success": True}

        except TemplateServiceError:
            raise
        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to create package.json: {e}",
                operation="create_package_json",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _create_main_js_file(
        self, project_path: Path, project_name: str, project_type: str
    ) -> dict[str, Any]:
        """Create the main JavaScript file.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            dict: Metadata about file creation with 'success' and 'files' keys

        Raises:
            ProjectServiceError: If main JavaScript file creation fails
        """
        try:
            src_dir = project_path / "src"
            src_dir.mkdir(exist_ok=True)

            created_files = []

            if project_type == "react":
                # Create React app structure
                react_files = self._create_react_structure(project_path, project_name)
                created_files.extend(react_files)
            elif project_type == "vue":
                # Create Vue app structure
                vue_files = self._create_vue_structure(project_path, project_name)
                created_files.extend(vue_files)
            else:
                # Create Node.js app structure
                node_files = self._create_node_structure(project_path, project_name)
                created_files.extend(node_files)

            return {"success": True, "files": created_files}

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to create main JavaScript file: {e}",
                operation="create_main_js_file",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _create_node_structure(
        self, project_path: Path, project_name: str
    ) -> list[str]:
        """Create Node.js project structure.

        Args:
            project_path: Path to the project
            project_name: Name of the project

        Returns:
            list: List of created file paths (relative to project_path)
        """
        src_dir = project_path / "src"
        created_files = []

        # Create main.js
        main_file = src_dir / "main.js"
        main_content = f"""#!/usr/bin/env node
/**
 * Main entry point for {project_name}.
 *
 * This module serves as the main entry point for the Node.js application.
 */

const path = require('path');
const fs = require('fs');

// Read package.json for version info
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf8'));

function main() {{
    console.log(`Hello from ${{packageJson.name}} v${{packageJson.version}}!`);
    console.log('This is a Node.js project created with WOMM CLI.');

    // Add your application logic here
    return 0;
}}

if (require.main === module) {{
    process.exit(main());
}}

module.exports = {{ main }};
"""
        main_file.write_text(main_content, encoding="utf-8")
        main_file.chmod(0o755)  # Make executable
        created_files.append(str(main_file.relative_to(project_path)))

        # Create index.js (entry point)
        index_file = src_dir / "index.js"
        index_content = f"""/**
 * Entry point for {project_name}.
 *
 * This file exports the main functionality of the application.
 */

const {{ main }} = require('./main');

module.exports = {{
    main,
    // Add other exports here
}};
"""
        index_file.write_text(index_content, encoding="utf-8")
        created_files.append(str(index_file.relative_to(project_path)))

        return created_files

    def _create_react_structure(
        self, project_path: Path, project_name: str
    ) -> list[str]:
        """Create React project structure.

        Args:
            project_path: Path to the project
            project_name: Name of the project

        Returns:
            list: List of created file paths (relative to project_path)
        """
        src_dir = project_path / "src"
        created_files = []

        # Create App.jsx
        app_file = src_dir / "App.jsx"
        app_content = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>This is a React project created with WOMM CLI.</p>
      </header>
    </div>
  );
}}

export default App;
"""
        app_file.write_text(app_content, encoding="utf-8")
        created_files.append(str(app_file.relative_to(project_path)))

        # Create App.css
        css_file = src_dir / "App.css"
        css_content = """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
}

.App-link {
  color: #61dafb;
}
"""
        css_file.write_text(css_content, encoding="utf-8")
        created_files.append(str(css_file.relative_to(project_path)))

        # Create index.jsx
        index_file = src_dir / "index.jsx"
        index_content = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        index_file.write_text(index_content, encoding="utf-8")
        created_files.append(str(index_file.relative_to(project_path)))

        # Create index.css
        index_css_file = src_dir / "index.css"
        index_css_content = """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
"""
        index_css_file.write_text(index_css_content, encoding="utf-8")
        created_files.append(str(index_css_file.relative_to(project_path)))

        # Create public/index.html
        public_dir = project_path / "public"
        public_dir.mkdir(exist_ok=True)

        html_file = public_dir / "index.html"
        html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="{project_name} - A React project created with WOMM CLI"
    />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
        html_file.write_text(html_content, encoding="utf-8")
        created_files.append(str(html_file.relative_to(project_path)))

        return created_files

    def _create_vue_structure(self, project_path: Path, project_name: str) -> list[str]:
        """Create Vue project structure.

        Args:
            project_path: Path to the project
            project_name: Name of the project

        Returns:
            list: List of created file paths (relative to project_path)
        """
        src_dir = project_path / "src"
        created_files = []

        # Create App.vue
        app_file = src_dir / "App.vue"
        app_content = f"""<template>
  <div id="app">
    <header>
      <h1>Welcome to {{ projectName }}</h1>
      <p>This is a Vue project created with WOMM CLI.</p>
    </header>
  </div>
</template>

<script>
export default {{
  name: 'App',
  data() {{
    return {{
      projectName: '{project_name}'
    }}
  }}
}}
</script>

<style>
#app {{
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}}

header {{
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}}
</style>
"""
        app_file.write_text(app_content, encoding="utf-8")
        created_files.append(str(app_file.relative_to(project_path)))

        # Create main.js
        main_file = src_dir / "main.js"
        main_content = """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
"""
        main_file.write_text(main_content, encoding="utf-8")
        created_files.append(str(main_file.relative_to(project_path)))

        # Create public/index.html
        public_dir = project_path / "public"
        public_dir.mkdir(exist_ok=True)

        html_file = public_dir / "index.html"
        html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <link rel="icon" href="<%= BASE_URL %>favicon.ico">
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>
      <strong>We're sorry but {project_name} doesn't work properly without JavaScript enabled. Please enable it to continue.</strong>
    </noscript>
    <div id="app"></div>
    <!-- built files will be auto injected -->
  </body>
</html>
"""
        html_file.write_text(html_content, encoding="utf-8")
        created_files.append(str(html_file.relative_to(project_path)))

        return created_files

    def _create_config_files(
        self, project_path: Path, _project_type: str
    ) -> dict[str, Any]:
        """Create configuration files.

        Args:
            project_path: Path to the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            dict: Metadata about file creation with 'success' and 'files' keys

        Raises:
            ProjectServiceError: If config files creation fails
        """
        try:
            created_files = []

            # Create .eslintrc.js
            eslint_config = """module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    'indent': ['error', 2],
    'linebreak-style': ['error', 'unix'],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
  },
};
"""
            eslint_file = project_path / ".eslintrc.js"
            eslint_file.write_text(eslint_config, encoding="utf-8")
            created_files.append(".eslintrc.js")

            # Create .prettierrc
            prettier_config = """{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
"""
            prettier_file = project_path / ".prettierrc"
            prettier_file.write_text(prettier_config, encoding="utf-8")
            created_files.append(".prettierrc")

            # Create jest.config.js for testing
            jest_config = """module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
};
"""
            jest_file = project_path / "jest.config.js"
            jest_file.write_text(jest_config, encoding="utf-8")
            created_files.append("jest.config.js")

            return {"success": True, "files": created_files}

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to create config files: {e}",
                operation="create_config_files",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _create_source_files(
        self, project_path: Path, _project_name: str, project_type: str
    ) -> dict[str, Any]:
        """Create source files based on project type.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            dict: Metadata about file creation with 'success' and 'files' keys

        Raises:
            ProjectServiceError: If source files creation fails
        """
        try:
            created_files = []

            if project_type == "react":
                # Create components directory
                components_dir = project_path / "src" / "components"
                components_dir.mkdir(exist_ok=True)

                # Create a sample component
                sample_component = components_dir / "SampleComponent.jsx"
                component_content = """import React from 'react';

function SampleComponent() {
  return (
    <div>
      <h2>Sample Component</h2>
      <p>This is a sample React component.</p>
    </div>
  );
}

export default SampleComponent;
"""
                sample_component.write_text(component_content, encoding="utf-8")
                created_files.append(str(sample_component.relative_to(project_path)))

            elif project_type == "vue":
                # Create components directory
                components_dir = project_path / "src" / "components"
                components_dir.mkdir(exist_ok=True)

                # Create a sample component
                sample_component = components_dir / "SampleComponent.vue"
                component_content = """<template>
  <div>
    <h2>Sample Component</h2>
    <p>This is a sample Vue component.</p>
  </div>
</template>

<script>
export default {
  name: 'SampleComponent'
}
</script>

<style scoped>
h2 {
  color: #42b983;
}
</style>
"""
                sample_component.write_text(component_content, encoding="utf-8")
                created_files.append(str(sample_component.relative_to(project_path)))

            else:  # node
                # Create utils directory
                utils_dir = project_path / "src" / "utils"
                utils_dir.mkdir(exist_ok=True)

                # Create a sample utility
                sample_util = utils_dir / "helpers.js"
                util_content = """/**
 * Utility functions for the application.
 */

/**
 * Format a message with the given prefix.
 * @param {string} prefix - The prefix to add to the message
 * @param {string} message - The message to format
 * @returns {string} The formatted message
 */
function formatMessage(prefix, message) {
  return `[${prefix}] ${message}`;
}

/**
 * Validate if a string is not empty.
 * @param {string} str - The string to validate
 * @returns {boolean} True if the string is not empty
 */
function isValidString(str) {
  return typeof str === 'string' && str.trim().length > 0;
}

module.exports = {
  formatMessage,
  isValidString,
};
"""
                sample_util.write_text(util_content, encoding="utf-8")
                created_files.append(str(sample_util.relative_to(project_path)))

            return {"success": True, "files": created_files}

        except Exception as e:
            raise ProjectServiceError(
                message=f"Failed to create source files: {e}",
                operation="create_source_files",
                details=f"Exception type: {type(e).__name__}",
            ) from e
