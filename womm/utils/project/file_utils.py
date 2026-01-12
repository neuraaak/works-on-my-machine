#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT FILE UTILS - Project File Creation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for creating project source files.

This module provides stateless functions for:
- Creating Python source files (main.py, __init__.py, test files)
- Creating JavaScript source files (main.js, components, etc.)
- File content generation
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectServiceError
from ...shared.configs.project.project_structure_config import ProjectStructureConfig

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PYTHON FILE CREATION
# ///////////////////////////////////////////////////////////////


def create_python_main_files(project_path: Path, project_name: str) -> list[str]:
    """Create Python main source files.

    Args:
        project_path: Path to the project
        project_name: Name of the project

    Returns:
        list[str]: List of created file paths (relative to project_path)

    Raises:
        ProjectServiceError: If file creation fails
    """
    try:
        # Create src directory structure
        src_dir = project_path / ProjectStructureConfig.SOURCE_DIR
        package_dir = src_dir / project_name.replace("-", "_")
        package_dir.mkdir(parents=True, exist_ok=True)

        created_files = []

        # Create __init__.py
        init_file = package_dir / "__init__.py"
        init_content = (
            f'"""Main package for {project_name}."""\n\n__version__ = "0.1.0"\n'
        )
        init_file.write_text(init_content, encoding="utf-8")
        created_files.append(str(init_file.relative_to(project_path)))

        # Create main.py
        main_file = package_dir / "main.py"
        main_content = f'''#!/usr/bin/env python3
"""
Main entry point for {project_name}.

This module serves as the main entry point for the application.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from {project_name.replace("-", "_")} import __version__


def main():
    """Main function."""
    print(f"Hello from {project_name} v{{__version__}}!")
    print("This is a Python project created with WOMM CLI.")

    # Add your application logic here
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
        main_file.write_text(main_content, encoding="utf-8")
        main_file.chmod(0o755)  # Make executable
        created_files.append(str(main_file.relative_to(project_path)))

        logger.debug(f"Created Python main files: {created_files}")
        return created_files

    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to create Python main files: {e}",
            operation="create_python_main_files",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def create_python_test_file(project_path: Path, project_name: str) -> list[str]:
    """Create Python test file.

    Args:
        project_path: Path to the project
        project_name: Name of the project

    Returns:
        list[str]: List of created file paths (relative to project_path)

    Raises:
        ProjectServiceError: If file creation fails
    """
    try:
        test_dir = project_path / ProjectStructureConfig.TESTS_DIR
        test_file = test_dir / f"test_{project_name.replace('-', '_')}.py"

        test_content = f'''"""
Tests for {project_name}.

This module contains tests for the main functionality.
"""

import pytest
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
import sys
sys.path.insert(0, str(src_path))

from {project_name.replace("-", "_")} import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_import():
    """Test that the package can be imported."""
    import {project_name.replace("-", "_")}
    assert {project_name.replace("-", "_")} is not None
'''
        test_file.write_text(test_content, encoding="utf-8")

        logger.debug(f"Created Python test file: {test_file.name}")
        return [str(test_file.relative_to(project_path))]

    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to create Python test file: {e}",
            operation="create_python_test_file",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT FILE CREATION
# ///////////////////////////////////////////////////////////////


def create_node_main_files(project_path: Path, project_name: str) -> list[str]:
    """Create Node.js main source files.

    Args:
        project_path: Path to the project
        project_name: Name of the project

    Returns:
        list[str]: List of created file paths (relative to project_path)

    Raises:
        ProjectServiceError: If file creation fails
    """
    try:
        src_dir = project_path / ProjectStructureConfig.SOURCE_DIR
        src_dir.mkdir(exist_ok=True)
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

        # Create index.js
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

        logger.debug(f"Created Node.js main files: {created_files}")
        return created_files

    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to create Node.js main files: {e}",
            operation="create_node_main_files",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def create_react_main_files(project_path: Path, project_name: str) -> list[str]:
    """Create React main source files.

    Args:
        project_path: Path to the project
        project_name: Name of the project

    Returns:
        list[str]: List of created file paths (relative to project_path)

    Raises:
        ProjectServiceError: If file creation fails
    """
    try:
        src_dir = project_path / ProjectStructureConfig.SOURCE_DIR
        src_dir.mkdir(exist_ok=True)
        public_dir = project_path / "public"
        public_dir.mkdir(exist_ok=True)
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

        logger.debug(f"Created React main files: {created_files}")
        return created_files

    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to create React main files: {e}",
            operation="create_react_main_files",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def create_vue_main_files(project_path: Path, project_name: str) -> list[str]:
    """Create Vue main source files.

    Args:
        project_path: Path to the project
        project_name: Name of the project

    Returns:
        list[str]: List of created file paths (relative to project_path)

    Raises:
        ProjectServiceError: If file creation fails
    """
    try:
        src_dir = project_path / ProjectStructureConfig.SOURCE_DIR
        src_dir.mkdir(exist_ok=True)
        public_dir = project_path / "public"
        public_dir.mkdir(exist_ok=True)
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

        logger.debug(f"Created Vue main files: {created_files}")
        return created_files

    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to create Vue main files: {e}",
            operation="create_vue_main_files",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def create_javascript_source_files(
    project_path: Path, project_name: str, project_type: str
) -> list[str]:
    """Create JavaScript source files based on project type.

    Args:
        project_path: Path to the project
        project_name: Name of the project
        project_type: Type of JavaScript project (node, react, vue)

    Returns:
        list[str]: List of created file paths (relative to project_path)

    Raises:
        ProjectServiceError: If file creation fails
    """
    try:
        if project_type == "react":
            return create_react_main_files(project_path, project_name)
        elif project_type == "vue":
            return create_vue_main_files(project_path, project_name)
        else:  # node
            return create_node_main_files(project_path, project_name)

    except ProjectServiceError:
        raise
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to create JavaScript source files: {e}",
            operation="create_javascript_source_files",
            details=f"Exception type: {type(e).__name__}, Project type: {project_type}",
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # File creation functions
    "create_javascript_source_files",
    "create_node_main_files",
    "create_python_main_files",
    "create_python_test_file",
    "create_react_main_files",
    "create_vue_main_files",
]
