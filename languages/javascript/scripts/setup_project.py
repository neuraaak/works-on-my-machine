#!/usr/bin/env python3
"""
JavaScript/Node.js development environment initialization script.

Usage:
    python setup_project.py [project_name] [--type=node|react|vue|vanilla]
    python setup_project.py --current-dir

Features:
    - Copy development configurations
    - Initialize Git with appropriate .gitignore
    - Configure pre-commit hooks
    - Create basic project structure
    - Configure VSCode and NPM
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Import security validator if available
try:
    from shared.security.security_validator import SecurityValidator

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


class JavaScriptProjectSetup:
    """Class to configure a JavaScript development environment."""

    PROJECT_TYPES = {
        "node": {
            "description": "Backend Node.js with Express",
            "main_file": "src/index.js",
            "module_type": "module",
            "dev_command": "nodemon src/index.js",
            "build_command": 'echo "No build needed for Node.js"',
            "start_command": "node src/index.js",
            "jest_environment": "node",
            "dependencies": '"express": "^4.18.0"',
            "dev_dependencies": '"nodemon": "^3.0.0", "supertest": "^6.3.0"',
            "keywords": "nodejs, express, api",
        },
        "react": {
            "description": "Frontend React with Vite",
            "main_file": "src/main.tsx",
            "module_type": "module",
            "dev_command": "vite",
            "build_command": "vite build",
            "start_command": "vite preview",
            "jest_environment": "jsdom",
            "dependencies": '"react": "^18.2.0", "react-dom": "^18.2.0"',
            "dev_dependencies": '"@vitejs/plugin-react": "^4.0.0", "vite": "^4.4.0", "@testing-library/react": "^13.4.0", "@testing-library/jest-dom": "^6.0.0"',
            "keywords": "react, frontend, vite",
        },
        "vue": {
            "description": "Frontend Vue.js with Vite",
            "main_file": "src/main.ts",
            "module_type": "module",
            "dev_command": "vite",
            "build_command": "vite build",
            "start_command": "vite preview",
            "jest_environment": "jsdom",
            "dependencies": '"vue": "^3.3.0"',
            "dev_dependencies": '"@vitejs/plugin-vue": "^4.3.0", "vite": "^4.4.0", "@vue/test-utils": "^2.4.0"',
            "keywords": "vue, frontend, vite",
        },
        "vanilla": {
            "description": "Vanilla JavaScript with bundler",
            "main_file": "src/index.js",
            "module_type": "module",
            "dev_command": "vite",
            "build_command": "vite build",
            "start_command": "vite preview",
            "jest_environment": "jsdom",
            "dependencies": "",
            "dev_dependencies": '"vite": "^4.4.0"',
            "keywords": "javascript, vanilla, vite",
        },
    }

    def __init__(
        self, project_path: Path, project_name: str, project_type: str = "node"
    ):
        """Initialize the JavaScript project configuration script."""
        self.project_path = project_path
        self.project_name = project_name
        self.project_type = project_type
        self.js_tools_path = Path(__file__).parent.parent
        self.devtools_path = self.js_tools_path.parent.parent

    def setup_all(self):
        """Configure the complete development environment."""
        print(f"🟨 Setting up JavaScript environment for '{self.project_name}'")
        print(f"📁 Directory: {self.project_path}")
        print(f"🎯 Type: {self.PROJECT_TYPES[self.project_type]['description']}")

        self.create_directory_structure()
        self.copy_configs()
        self.setup_git()
        self.setup_cspell()
        self.create_package_json()
        self.create_project_files()
        self.setup_vscode()
        self.setup_development_environment()
        self.install_dependencies()

        print("\n✅ JavaScript configuration completed!")
        self.print_next_steps()

    def create_directory_structure(self):
        """Create the basic directory structure."""
        print("\n📂 Creating directory structure...")

        directories = [
            self.project_path / "src",
            self.project_path / "tests",
            self.project_path / "docs",
            self.project_path / ".vscode",
        ]

        # Type-specific directories
        if self.project_type in ["react", "vue"]:
            directories.extend(
                [
                    self.project_path / "public",
                    self.project_path / "src" / "components",
                    self.project_path / "src" / "assets",
                ]
            )

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ {directory}")

    def copy_configs(self):
        """Copy configuration files."""
        print("\n⚙️ Copying JavaScript configurations...")

        configs = [
            ("configs/.eslintrc.json", ".eslintrc.json"),
            ("configs/prettier.config.js", "prettier.config.js"),
            ("templates/gitignore-node.txt", ".gitignore"),
        ]

        for source, dest in configs:
            source_path = self.js_tools_path / source
            dest_path = self.project_path / dest

            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"   ✓ {dest}")
            else:
                print(f"   ⚠️  Missing file: {source}")

    def setup_git(self):
        """Initialize Git and configure .gitignore."""
        print("\n🔧 Configuring Git...")

        if not (self.project_path / ".git").exists():
            try:
                git_path = shutil.which("git")
                if git_path is None:
                    print("   ⚠️  Git not found")
                    return

                # Security validation
                if SECURITY_AVAILABLE:
                    validator = SecurityValidator()
                    is_valid, error_msg = validator.validate_command([git_path, "init"])
                    if not is_valid:
                        print(f"   ⚠️  Security validation failed: {error_msg}")
                        return

                subprocess.run(  # noqa: S603
                    [git_path, "init"],
                    cwd=self.project_path,
                    check=True,
                    capture_output=True,
                )
                print("   ✓ Git repository initialized")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("   ⚠️  Git not found or initialization error")

    def setup_cspell(self):
        """Configure CSpell for the project."""
        print("📝 Configuring CSpell...")

        # Importer le gestionnaire CSpell
        devtools_path = Path.home() / ".womm"
        sys.path.insert(0, str(devtools_path))

        try:
            from shared.tools.cspell_manager import setup_project_cspell

            success = setup_project_cspell(
                self.project_path, "javascript", self.project_name
            )
            if success:
                print("   ✓ CSpell configuration created")
            else:
                print("   ⚠ Error during CSpell configuration")
        except ImportError:
            print("   ⚠ cspell_manager module not found")

    def setup_development_environment(self):
        """Configure the JavaScript development environment."""
        print("🛠️ Setting up development environment...")

        # Importer le gestionnaire d'environnement
        devtools_path = Path.home() / ".womm"
        sys.path.insert(0, str(devtools_path))

        try:
            from shared.project.environment_manager import EnvironmentManager

            manager = EnvironmentManager(self.project_path, "javascript")

            if manager.prompt_install_tools():
                if manager.setup_javascript_environment():
                    manager.create_activation_scripts()
                    print("   ✓ Development environment configured")
                    return True
                else:
                    print("   ⚠ Error configuring development environment")
                    return False
            else:
                print("   ⏭️ Development environment setup skipped")
                return True

        except ImportError:
            print("   ⚠ environment_manager module not found")
            return False

    def create_package_json(self):
        """Create the package.json file."""
        print("\n📦 Creating package.json...")

        template_path = self.js_tools_path / "templates" / "package.template.json"
        if not template_path.exists():
            print("   ⚠️  package.json template missing")
            return

        # Read template
        template_content = template_path.read_text(encoding="utf-8")

        # Replace placeholders
        config = self.PROJECT_TYPES[self.project_type]
        replacements = {
            "{{PROJECT_NAME}}": self.project_name,
            "{{MAIN_FILE}}": config["main_file"],
            "{{MODULE_TYPE}}": config["module_type"],
            "{{DEV_COMMAND}}": config["dev_command"],
            "{{BUILD_COMMAND}}": config["build_command"],
            "{{START_COMMAND}}": config["start_command"],
            "{{JEST_ENVIRONMENT}}": config["jest_environment"],
            "{{DEPENDENCIES}}": config["dependencies"],
            "{{DEV_DEPENDENCIES}}": config["dev_dependencies"],
            "{{KEYWORDS}}": config["keywords"],
        }

        for placeholder, value in replacements.items():
            template_content = template_content.replace(placeholder, value)

        # Clean up extra commas
        template_content = template_content.replace(",\n    \n  }", "\n  }")
        template_content = template_content.replace(",\n    {{", "\n    {{")

        # Write file
        (self.project_path / "package.json").write_text(
            template_content, encoding="utf-8"
        )
        print("   ✓ package.json")

    def create_project_files(self):
        """Create basic project files based on type."""
        print("\n📄 Creating basic files...")

        # README.md
        readme_content = f"""# {self.project_name}

{self.PROJECT_TYPES[self.project_type]["description"]}

## 🚀 Installation

```bash
npm install
```

## 🛠️ Development

```bash
# Development server
npm run dev

# Production build
npm run build

# Tests
npm test
npm run test:coverage

# Linting and formatting
npm run lint
npm run format
```

## 📋 Available Scripts

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run start` - Production server
- `npm run lint` - ESLint checking
- `npm run format` - Prettier formatting
- `npm test` - Jest tests

## 📖 Documentation

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the complete development guide.
"""
        (self.project_path / "README.md").write_text(readme_content, encoding="utf-8")
        print("   ✓ README.md")

        # Create type-specific files
        self._create_type_specific_files()

        # TypeScript config (if needed)
        if self.project_type != "vanilla":
            self._create_typescript_config()

        # Test example
        self._create_test_files()

    def _create_type_specific_files(self):
        """Create type-specific project files."""
        if self.project_type == "node":
            # src/index.js
            index_content = """import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Hello World! 🚀' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});

export default app;
"""
            (self.project_path / "src" / "index.js").write_text(
                index_content, encoding="utf-8"
            )

        elif self.project_type == "react":
            # src/main.tsx
            main_content = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
"""
            (self.project_path / "src" / "main.tsx").write_text(
                main_content, encoding="utf-8"
            )

            # src/App.tsx
            app_content = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Welcome to {self.project_name}</h1>
        <p>Your React app is ready!</p>
      </header>
    </div>
  );
}}

export default App;
"""
            (self.project_path / "src" / "App.tsx").write_text(
                app_content, encoding="utf-8"
            )

            # index.html
            html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{self.project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
            (self.project_path / "index.html").write_text(
                html_content, encoding="utf-8"
            )

        elif self.project_type == "vue":
            # src/main.ts
            main_content = """import { createApp } from 'vue';
import App from './App.vue';
import './style.css';

createApp(App).mount('#app');
"""
            (self.project_path / "src" / "main.ts").write_text(
                main_content, encoding="utf-8"
            )

        print(f"   ✓ {self.project_type} files created")

    def _create_typescript_config(self):
        """Create TypeScript configuration."""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}],
        }

        if self.project_type == "react":
            tsconfig["compilerOptions"]["jsx"] = "react-jsx"

        (self.project_path / "tsconfig.json").write_text(
            json.dumps(tsconfig, indent=2), encoding="utf-8"
        )
        print("   ✓ tsconfig.json")

    def _create_test_files(self):
        """Create example test files."""
        if self.project_type == "node":
            test_content = """import request from 'supertest';
import app from '../src/index.js';

describe('API Tests', () => {
  test('GET / should return welcome message', async () => {
    const response = await request(app)
      .get('/')
      .expect(200);

    expect(response.body.message).toBe('Hello World! 🚀');
  });

  test('GET /health should return status OK', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);

    expect(response.body.status).toBe('OK');
  });
});
"""
        else:
            test_content = f"""import {{ render, screen }} from '@testing-library/react';
import App from '../src/App';

describe('App Component', () => {{
  test('renders welcome message', () => {{
    render(<App />);
    const linkElement = screen.getByText(/Welcome to {self.project_name}/i);
    expect(linkElement).toBeInTheDocument();
  }});
}});
"""

        (self.project_path / "tests" / f"{self.project_name}.test.js").write_text(
            test_content, encoding="utf-8"
        )
        print("   ✓ Test files")

    def setup_vscode(self):
        """Configure VSCode."""
        print("\n🔧 Configuring VSCode...")

        vscode_files = ["settings.json", "extensions.json"]

        for file in vscode_files:
            source = self.js_tools_path / "vscode" / file
            dest = self.project_path / ".vscode" / file

            if source.exists():
                shutil.copy2(source, dest)
                print(f"   ✓ .vscode/{file}")
            else:
                print(f"   ⚠️  Missing VSCode file: {file}")

    def install_dependencies(self):
        """Install NPM dependencies."""
        print("\n📦 Installing dependencies...")

        try:
            # Check npm
            npm_path = shutil.which("npm")
            if npm_path is None:
                print("   ⚠️  npm not found. Install Node.js/npm")
                return

            # Security validation
            if SECURITY_AVAILABLE:
                validator = SecurityValidator()
                is_valid, error_msg = validator.validate_command(
                    [npm_path, "--version"]
                )
                if not is_valid:
                    print(f"   ⚠️  Security validation failed: {error_msg}")
                    return

            subprocess.run(  # noqa: S603
                [npm_path, "--version"], capture_output=True, check=True
            )

            # Install dependencies
            print("   🔄 Installing...")
            # Security validation
            if SECURITY_AVAILABLE:
                validator = SecurityValidator()
                is_valid, error_msg = validator.validate_command([npm_path, "install"])
                if not is_valid:
                    print(f"   ⚠️  Security validation failed: {error_msg}")
                    return

            result = subprocess.run(  # noqa: S603
                [npm_path, "install"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("   ✅ Dependencies installed")

                # Install husky
                npx_path = shutil.which("npx")
                if npx_path is not None:
                    # Security validation
                    if SECURITY_AVAILABLE:
                        validator = SecurityValidator()
                        is_valid, error_msg = validator.validate_command(
                            [npx_path, "husky", "install"]
                        )
                        if not is_valid:
                            print(f"   ⚠️  Security validation failed: {error_msg}")
                            return

                    subprocess.run(  # noqa: S603
                        [npx_path, "husky", "install"],
                        cwd=self.project_path,
                        capture_output=True,
                    )
                    print("   ✅ Husky hooks configured")
                else:
                    print("   ⚠️  npx not found, skipping husky installation")
            else:
                print(f"   ⚠️  Installation error: {result.stderr}")

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ⚠️  npm not found. Install Node.js/npm")

    def print_next_steps(self):
        """Display next steps."""
        print(
            f"""
🎉 JavaScript project '{self.project_name}' configured successfully!

📋 Next steps:
1. cd {self.project_path}
2. npm install  # If not already done
3. npm run dev  # Start development server
4. git add .
5. git commit -m "Initial commit with JS dev environment"

🛠️ Useful commands:
- npm run dev              # Development server
- npm run build            # Production build
- npm run lint             # ESLint check
- npm run format           # Prettier formatting
- npm test                 # Jest tests

📚 Documentation:
- docs/DEVELOPMENT.md      # Development guide
- {self.js_tools_path}/JAVASCRIPT.md  # Complete JavaScript documentation

🟨 Happy JavaScript coding!
"""
        )


def main():
    """Execute the main function."""
    parser = argparse.ArgumentParser(
        description="Configure a JavaScript development environment"
    )
    parser.add_argument(
        "project_name", nargs="?", help="Project name (optional if --current-dir)"
    )
    parser.add_argument(
        "--current-dir",
        action="store_true",
        help="Configure current directory instead of creating a new one",
    )
    parser.add_argument(
        "--type",
        choices=["node", "react", "vue", "vanilla"],
        default="node",
        help="JavaScript project type (default: node)",
    )

    args = parser.parse_args()

    if args.current_dir:
        project_path = Path.cwd()
        project_name = project_path.name
    elif args.project_name:
        project_name = args.project_name
        project_path = Path.cwd() / project_name
    else:
        project_name = input("JavaScript project name: ").strip()
        if not project_name:
            print("❌ Project name required")
            return 1
        project_path = Path.cwd() / project_name

    # Type selection if not specified
    if not args.current_dir and not args.type:
        print("\n🎯 What type of JavaScript project do you want to create?")
        for i, (key, config) in enumerate(
            JavaScriptProjectSetup.PROJECT_TYPES.items(), 1
        ):
            print(f"{i}. {key} - {config['description']}")

        try:
            choice = int(input("Choice (1-4): ")) - 1
            project_type = list(JavaScriptProjectSetup.PROJECT_TYPES.keys())[choice]
        except (ValueError, IndexError):
            project_type = "node"
    else:
        project_type = args.type

    # Confirm before continuing
    if not args.current_dir:
        response = input(
            f"Create JavaScript project '{project_name}' ({project_type}) in {project_path}? (y/N): "
        )
        if response.lower() not in ("y", "yes", "o", "oui"):
            print("Cancelled.")
            return 0

    setup = JavaScriptProjectSetup(project_path, project_name, project_type)
    setup.setup_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
