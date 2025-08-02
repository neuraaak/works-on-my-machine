#!/usr/bin/env python3
"""
Development environment manager.
Automatically creates and configures virtual environments and dependencies.
"""

import json
import platform
import shutil
import venv
from pathlib import Path
from typing import Optional

# Import CLI manager
from shared.core.cli_manager import (
    run_command,
    run_silent,
)


class EnvironmentManager:
    """Development environment manager."""

    def __init__(self, project_path: Path, project_type: str):
        """Initialize the development environment manager."""
        self.project_path = Path(project_path)
        self.project_type = project_type
        self.system = platform.system()

    def prompt_install_tools(self) -> bool:
        """Ask the user if they want to install the tools."""
        print("\n🛠️  Development environment configuration")
        print("=" * 55)

        if self.project_type == "python":
            print("📦 Python tools to install:")
            print("  • Virtual environment (venv)")
            print("  • black (formatting)")
            print("  • flake8 (linting)")
            print("  • isort (import organization)")
            print("  • pytest (testing)")
            print("  • pre-commit (hooks)")
            print("  • mypy (type checking)")

        elif self.project_type == "javascript":
            print("📦 JavaScript tools to install:")
            print("  • eslint (linting)")
            print("  • prettier (formatting)")
            print("  • typescript (if TypeScript)")
            print("  • jest (testing)")
            print("  • husky (hooks)")

        response = input("\n🤔 Install development tools? (Y/n): ").lower()
        return response in ["", "y", "yes"]

    def setup_python_environment(self) -> bool:
        """Set up the complete Python environment."""
        success = True

        try:
            # 1. Create virtual environment
            if self.create_virtual_environment():
                print("   ✓ Virtual environment created")
            else:
                print("   ⚠ Error creating venv")
                success = False

            # 2. Install development tools
            if self.install_python_tools():
                print("   ✓ Python tools installed")
            else:
                print("   ⚠ Error installing tools")
                success = False

            # 3. Install pre-commit hooks
            if self.setup_pre_commit():
                print("   ✓ Pre-commit hooks configured")
            else:
                print("   ⚠ Error configuring pre-commit")

            return success

        except Exception as e:
            print(f"   ❌ Error during Python setup: {e}")
            return False

    def create_virtual_environment(self) -> bool:
        """Create a Python virtual environment."""
        venv_path = self.project_path / "venv"

        if venv_path.exists():
            print("   ℹ️  Existing virtual environment detected")
            return True

        try:
            print("   📦 Creating virtual environment...")

            # Create venv
            venv.create(venv_path, with_pip=True)

            # Check creation
            if self.system == "Windows":
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:
                python_exe = venv_path / "bin" / "python"
                pip_exe = venv_path / "bin" / "pip"

            if python_exe.exists() and pip_exe.exists():
                # Update pip
                result = run_command(
                    [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
                    "Updating pip",
                )
                if not result.success:
                    print("   ⚠️ Error updating pip")
                return True
            else:
                print("   ❌ Executables not found after creation")
                return False

        except Exception as e:
            print(f"   ❌ Error creating venv: {e}")
            return False

    def get_venv_python(self) -> Optional[Path]:
        """Return the path to the venv Python executable."""
        venv_path = self.project_path / "venv"

        if self.system == "Windows":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"

        return python_exe if python_exe.exists() else None

    def get_venv_pip(self) -> Optional[Path]:
        """Return the path to the venv pip executable."""
        venv_path = self.project_path / "venv"

        if self.system == "Windows":
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            pip_exe = venv_path / "bin" / "pip"

        return pip_exe if pip_exe.exists() else None

    def install_python_tools(self) -> bool:
        """Install Python development tools."""
        python_exe = self.get_venv_python()

        if not python_exe:
            print("   ❌ Virtual environment not found")
            return False

        # Essential tools
        dev_tools = [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pre-commit>=3.0.0",
            "mypy>=1.0.0",
        ]

        # Optional tools depending on project
        optional_tools = [
            "bandit>=1.7.0",  # Security
            "coverage>=7.0.0",  # Coverage
            "sphinx>=6.0.0",  # Documentation
            "wheel>=0.40.0",  # Build
        ]

        try:
            print("   📥 Installing essential tools...")

            # Install essential tools
            cmd = [str(python_exe), "-m", "pip", "install"] + dev_tools
            result = run_command(cmd, "Installing essential Python tools")
            if not result.success:
                print("   ❌ Error installing essential tools")
                return False

            print("   📥 Installing optional tools...")

            # Install optional tools (non-blocking)
            cmd_optional = [str(python_exe), "-m", "pip", "install"] + optional_tools
            run_silent(cmd_optional)

            return True

        except Exception as e:
            print(f"   ❌ Error during pip install: {e}")
            return False

    def setup_pre_commit(self) -> bool:
        """Configure pre-commit hooks."""
        python_exe = self.get_venv_python()
        pre_commit_config = self.project_path / ".pre-commit-config.yaml"

        if not python_exe or not pre_commit_config.exists():
            return False

        try:
            # Install hooks
            cmd = [str(python_exe), "-m", "pre_commit", "install"]
            result = run_command(
                cmd, "Installing pre-commit hooks", cwd=self.project_path
            )

            return result.success

        except Exception:
            return False

    def setup_javascript_environment(self) -> bool:
        """Set up the complete JavaScript environment."""
        success = True

        try:
            # Check if npm is available
            if not shutil.which("npm"):
                print("   ❌ npm not found - install Node.js first")
                return False

            # 1. Install npm dependencies
            if self.install_javascript_tools():
                print("   ✓ JavaScript tools installed")
            else:
                print("   ⚠ Error installing tools")
                success = False

            # 2. Configure husky (hooks)
            if self.setup_husky():
                print("   ✓ Husky configured")
            else:
                print("   ⚠ Error configuring husky")

            return success

        except Exception as e:
            print(f"   ❌ Error during JavaScript setup: {e}")
            return False

    def install_javascript_tools(self) -> bool:
        """Install JavaScript development tools."""
        package_json = self.project_path / "package.json"

        if not package_json.exists():
            print("   ❌ package.json not found")
            return False

        # Read package.json to detect TypeScript
        try:
            with open(package_json, encoding="utf-8") as f:
                pkg_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pkg_data = {}

        is_typescript = (
            "typescript" in pkg_data.get("dependencies", {})
            or "typescript" in pkg_data.get("devDependencies", {})
            or (self.project_path / "tsconfig.json").exists()
        )

        # Essential tools
        dev_tools = [
            "eslint",
            "prettier",
            "@eslint/js",
            "eslint-config-prettier",
            "eslint-plugin-prettier",
        ]

        # TypeScript tools
        if is_typescript:
            dev_tools.extend(
                [
                    "typescript",
                    "@typescript-eslint/parser",
                    "@typescript-eslint/eslint-plugin",
                    "@types/node",
                ]
            )

        # Testing tools
        test_tools = ["jest", "@jest/globals"]

        if is_typescript:
            test_tools.extend(["ts-jest", "@types/jest"])

        # Hooks
        hook_tools = ["husky", "lint-staged"]

        try:
            print("   📥 Installing development tools...")

            # Install essential tools
            cmd = ["npm", "install", "--save-dev"] + dev_tools
            result = run_command(
                cmd, "Installing essential JavaScript tools", cwd=self.project_path
            )
            if not result.success:
                print("   ❌ Error installing essential tools")
                return False

            print("   📥 Installing testing tools...")

            # Install testing tools
            cmd_test = ["npm", "install", "--save-dev"] + test_tools
            result = run_command(
                cmd_test, "Installing testing tools", cwd=self.project_path
            )
            if not result.success:
                print("   ❌ Error installing testing tools")
                return False

            print("   📥 Installing hooks...")

            # Install hooks
            cmd_hooks = ["npm", "install", "--save-dev"] + hook_tools
            result = run_command(
                cmd_hooks, "Installing JavaScript hooks", cwd=self.project_path
            )
            if not result.success:
                print("   ❌ Error installing hooks")
                return False

            return True

        except Exception as e:
            print(f"   ❌ Error during npm install: {e}")
            return False

    def setup_husky(self) -> bool:
        """Configure husky for Git hooks."""
        try:
            # Initialize husky
            cmd = ["npx", "husky", "install"]
            result = run_command(cmd, "Initializing husky", cwd=self.project_path)
            if not result.success:
                print("   ❌ Error initializing husky")
                return False

            # Add pre-commit hook
            hook_cmd = ["npx", "husky", "add", ".husky/pre-commit", "npm run lint"]
            run_silent(hook_cmd, cwd=self.project_path)

            return True

        except Exception:
            return False

    def create_activation_scripts(self) -> bool:
        """Create environment activation scripts."""
        if self.project_type == "python":
            return self.create_python_activation_scripts()
        elif self.project_type == "javascript":
            return self.create_javascript_activation_scripts()
        return False

    def create_python_activation_scripts(self) -> bool:
        """Create Python activation scripts."""
        try:
            # Script Windows
            if self.system == "Windows":
                activate_script = self.project_path / "activate.bat"
                script_content = f"""@echo off
echo 🐍 Activating Python environment for {self.project_path.name}
call venv\\Scripts\\activate.bat
echo ✅ Environment activated - use 'deactivate' to exit
"""
                activate_script.write_text(script_content, encoding="utf-8")

            # Script Unix
            activate_script_sh = self.project_path / "activate.sh"
            script_content_sh = f"""#!/bin/bash
echo "🐍 Activating Python environment for {self.project_path.name}"
source venv/bin/activate
echo "✅ Environment activated - use 'deactivate' to exit"
"""
            activate_script_sh.write_text(script_content_sh, encoding="utf-8")
            activate_script_sh.chmod(0o755)

            return True

        except Exception as e:
            print(f"   ⚠ Error creating activation scripts: {e}")
            return False

    def create_javascript_activation_scripts(self) -> bool:
        """Create useful JavaScript scripts."""
        try:
            # Windows development script
            if self.system == "Windows":
                dev_script = self.project_path / "dev.bat"
                script_content = f"""@echo off
echo 🟨 Starting JavaScript environment for {self.project_path.name}
echo 📦 Installing dependencies...
npm install
echo 🚀 Starting development server...
npm run dev
"""
                dev_script.write_text(script_content, encoding="utf-8")

            # Script Unix
            dev_script_sh = self.project_path / "dev.sh"
            script_content_sh = f"""#!/bin/bash
echo "🟨 Starting JavaScript environment for {self.project_path.name}"
echo "📦 Installing dependencies..."
npm install
echo "🚀 Starting development server..."
npm run dev
"""
            dev_script_sh.write_text(script_content_sh, encoding="utf-8")
            dev_script_sh.chmod(0o755)

            return True

        except Exception as e:
            print(f"   ⚠ Error creating development scripts: {e}")
            return False

    def print_environment_info(self):
        """Display information about the created environment."""
        print("\n🎉 Development environment configured!")
        print("=" * 50)

        if self.project_type == "python":
            venv_path = self.project_path / "venv"
            if venv_path.exists():
                print(f"📁 Virtual environment: {venv_path}")
                if self.system == "Windows":
                    print("🚀 Activation: activate.bat")
                    print("🐍 Python: .\\venv\\Scripts\\python.exe")
                else:
                    print("🚀 Activation: source activate.sh")
                    print("🐍 Python: ./venv/bin/python")

                print("\n🛠️ Installed tools:")
                print("  • black (formatting)")
                print("  • flake8 (linting)")
                print("  • isort (imports)")
                print("  • pytest (testing)")
                print("  • pre-commit (hooks)")
                print("  • mypy (types)")

        elif self.project_type == "javascript":
            node_modules = self.project_path / "node_modules"
            if node_modules.exists():
                print(f"📁 Node modules: {node_modules}")
                print("🚀 Development: npm run dev")
                print("🟨 Node.js: npm")

                print("\n🛠️ Installed tools:")
                print("  • eslint (linting)")
                print("  • prettier (formatting)")
                print("  • jest (testing)")
                print("  • husky (hooks)")

        print("\n💡 Next steps:")
        if self.project_type == "python":
            print("  1. Activate environment: activate.bat")
            print("  2. Run tests: pytest")
            print("  3. Format code: black .")
        elif self.project_type == "javascript":
            print("  1. Start project: npm run dev")
            print("  2. Run tests: npm test")
            print("  3. Lint code: npm run lint")


def main():
    """Run the main entry point for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Development environment manager")
    parser.add_argument("project_path", help="Project path")
    parser.add_argument(
        "project_type", choices=["python", "javascript"], help="Project type"
    )
    parser.add_argument(
        "--no-prompt", action="store_true", help="Install without asking"
    )

    args = parser.parse_args()

    manager = EnvironmentManager(Path(args.project_path), args.project_type)

    if args.no_prompt or manager.prompt_install_tools():
        if args.project_type == "python":
            success = manager.setup_python_environment()
        else:
            success = manager.setup_javascript_environment()

        if success:
            manager.create_activation_scripts()
            manager.print_environment_info()
        else:
            print("❌ Error configuring environment")
    else:
        print("⏭️ Environment configuration skipped")


if __name__ == "__main__":
    main()
