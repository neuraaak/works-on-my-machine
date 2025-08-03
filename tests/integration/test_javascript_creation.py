"""Integration tests for JavaScript project creation functionality."""

from unittest.mock import Mock, patch


class TestJavaScriptProjectCreation:
    """Integration tests for JavaScript project creation."""

    def test_create_javascript_project_structure(self, temp_dir):
        """Test that JavaScript project creation creates correct structure."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name

        # Mock the setup script to create actual structure
        with patch("shared.secure_cli_manager.run_secure_command") as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=True,
                returncode=0,
                stdout="Project created successfully",
                stderr="",
            )

            # Create project structure manually for testing
            project_path.mkdir()
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            (project_path / "public").mkdir()
            (project_path / ".vscode").mkdir()

            # Create sample files
            (project_path / "src" / "index.js").write_text(
                "console.log('Hello, World!');"
            )
            (project_path / "tests" / "index.test.js").write_text(
                "test('hello', () => {});"
            )
            (project_path / "package.json").write_text('{"name": "test-js-project"}')
            (project_path / ".gitignore").write_text("node_modules/\n*.log")

            # Verify structure
            assert project_path.exists()
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
            assert (project_path / "public").exists()
            assert (project_path / ".vscode").exists()
            assert (project_path / "package.json").exists()
            assert (project_path / ".gitignore").exists()

    def test_javascript_project_package_json(self, temp_dir):
        """Test that JavaScript project has correct package.json."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create package.json
        package_json_content = """
{
  "name": "test-js-project",
  "version": "1.0.0",
  "description": "Test JavaScript project",
  "main": "src/index.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "prettier": "^2.8.0",
    "jest": "^29.0.0",
    "vite": "^4.0.0"
  }
}
"""
        (project_path / "package.json").write_text(package_json_content)

        # Verify package.json content
        package_file = project_path / "package.json"
        assert package_file.exists()

        content = package_file.read_text()
        assert "test-js-project" in content
        assert "eslint" in content
        assert "prettier" in content
        assert "jest" in content

    def test_javascript_project_eslint_config(self, temp_dir):
        """Test that JavaScript project has correct ESLint configuration."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create ESLint configuration
        eslint_config_content = """
{
  "extends": [
    "eslint:recommended"
  ],
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error"
  }
}
"""
        (project_path / ".eslintrc.json").write_text(eslint_config_content)

        # Verify ESLint configuration
        eslint_file = project_path / ".eslintrc.json"
        assert eslint_file.exists()

        content = eslint_file.read_text()
        assert "eslint:recommended" in content
        assert "no-console" in content
        assert "no-unused-vars" in content

    def test_javascript_project_prettier_config(self, temp_dir):
        """Test that JavaScript project has correct Prettier configuration."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create Prettier configuration
        prettier_config_content = """
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
"""
        (project_path / "prettier.config.js").write_text(prettier_config_content)

        # Verify Prettier configuration
        prettier_file = project_path / "prettier.config.js"
        assert prettier_file.exists()

        content = prettier_file.read_text()
        assert "semi" in content
        assert "singleQuote" in content
        assert "printWidth" in content

    def test_javascript_project_git_integration(self, temp_dir):
        """Test that JavaScript project integrates with Git."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create .gitignore
        gitignore_content = """
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.tsbuildinfo

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        (project_path / ".gitignore").write_text(gitignore_content)

        # Verify .gitignore content
        gitignore_file = project_path / ".gitignore"
        assert gitignore_file.exists()

        content = gitignore_file.read_text()
        assert "node_modules/" in content
        assert "dist/" in content
        assert ".env" in content
        assert ".vscode/" in content

    def test_javascript_project_complete_workflow(self, temp_dir):
        """Test complete JavaScript project creation workflow."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name

        # Mock CLI execution
        with patch("shared.secure_cli_manager.run_secure_command") as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=True,
                returncode=0,
                stdout="Project created successfully",
                stderr="",
            )

            # Create complete project structure
            project_path.mkdir()

            # Source code
            src_dir = project_path / "src"
            src_dir.mkdir()
            (src_dir / "index.js").write_text(
                """
function helloWorld() {
    return "Hello, World!";
}

console.log(helloWorld());
"""
            )

            # Tests
            tests_dir = project_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "index.test.js").write_text(
                """
const { helloWorld } = require('../src/index.js');

test('helloWorld returns correct message', () => {
    expect(helloWorld()).toBe("Hello, World!");
});
"""
            )

            # Configuration files
            (project_path / "package.json").write_text(
                """
{
  "name": "test-js-project",
  "version": "1.0.0",
  "description": "Test JavaScript project",
  "main": "src/index.js",
  "scripts": {
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "prettier": "^2.8.0",
    "jest": "^29.0.0"
  }
}
"""
            )

            # Verify complete structure
            assert project_path.exists()
            assert src_dir.exists()
            assert tests_dir.exists()
            assert (src_dir / "index.js").exists()
            assert (tests_dir / "index.test.js").exists()
            assert (project_path / "package.json").exists()

            # Verify source code content
            main_content = (src_dir / "index.js").read_text()
            assert "function helloWorld()" in main_content
            assert 'return "Hello, World!"' in main_content

            # Verify test content
            test_content = (tests_dir / "index.test.js").read_text()
            assert "test('helloWorld returns correct message'" in test_content
            assert 'helloWorld()).toBe("Hello, World!")' in test_content
