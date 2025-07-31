#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'initialisation d'environnement de développement JavaScript/Node.js.

Usage:
    python setup_project.py [nom_projet] [--type=node|react|vue|vanilla]
    python setup_project.py --current-dir

Fonctionnalités:
    - Copie les configurations de développement
    - Initialise Git avec .gitignore adapté
    - Configure les hooks pre-commit
    - Crée la structure de projet de base
    - Configure VSCode et NPM
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


class JavaScriptProjectSetup:
    """Classe pour configurer un environnement de développement JavaScript."""

    PROJECT_TYPES = {
        "node": {
            "description": "Backend Node.js avec Express",
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
            "description": "Frontend React avec Vite",
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
            "description": "Frontend Vue.js avec Vite",
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
            "description": "JavaScript vanilla avec bundler",
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
        """Initialise le script de configuration du projet JavaScript."""
        self.project_path = project_path
        self.project_name = project_name
        self.project_type = project_type
        self.js_tools_path = Path(__file__).parent.parent
        self.devtools_path = self.js_tools_path.parent.parent

    def setup_all(self):
        """Configure tout l'environnement de développement."""
        print(
            f"🟨 Configuration de l'environnement JavaScript pour '{self.project_name}'"
        )
        print(f"📁 Répertoire: {self.project_path}")
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

        print("\n✅ Configuration JavaScript terminée !")
        self.print_next_steps()

    def create_directory_structure(self):
        """Crée la structure de répertoires de base."""
        print("\n📂 Création de la structure de répertoires...")

        directories = [
            self.project_path / "src",
            self.project_path / "tests",
            self.project_path / "docs",
            self.project_path / ".vscode",
        ]

        # Dossiers spécifiques selon le type
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
        print("\n⚙️ Copie des configurations JavaScript...")

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
                print(f"   ⚠️  Fichier manquant: {source}")

    def setup_git(self):
        """Initialise Git et configure .gitignore."""
        print("\n🔧 Configuration Git...")

        if not (self.project_path / ".git").exists():
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=self.project_path,
                    check=True,
                    capture_output=True,
                )
                print("   ✓ Repository Git initialisé")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("   ⚠️  Git non trouvé ou erreur d'initialisation")

    def setup_cspell(self):
        """Configure CSpell pour le projet."""
        print("📝 Configuration CSpell...")

        # Importer le gestionnaire CSpell
        devtools_path = Path.home() / ".dev-tools"
        sys.path.insert(0, str(devtools_path))

        try:
            from shared.cspell_manager import setup_project_cspell

            success = setup_project_cspell(
                self.project_path, "javascript", self.project_name
            )
            if success:
                print("   ✓ Configuration CSpell créée")
            else:
                print("   ⚠ Erreur lors de la configuration CSpell")
        except ImportError:
            print("   ⚠ Module cspell_manager non trouvé")

    def setup_development_environment(self):
        """Configure l'environnement de développement JavaScript."""
        print("🛠️ Configuration de l'environnement de développement...")

        # Importer le gestionnaire d'environnement
        devtools_path = Path.home() / ".dev-tools"
        sys.path.insert(0, str(devtools_path))

        try:
            from shared.environment_manager import EnvironmentManager

            manager = EnvironmentManager(self.project_path, "javascript")

            if manager.prompt_install_tools():
                if manager.setup_javascript_environment():
                    manager.create_activation_scripts()
                    print("   ✓ Environnement de développement configuré")
                    return True
                else:
                    print("   ⚠ Erreur lors de la configuration de l'environnement")
                    return False
            else:
                print("   ⏭️ Configuration de l'environnement ignorée")
                return True

        except ImportError:
            print("   ⚠ Module environment_manager non trouvé")
            return False

    def create_package_json(self):
        """Crée le fichier package.json."""
        print("\n📦 Création du package.json...")

        template_path = self.js_tools_path / "templates" / "package.template.json"
        if not template_path.exists():
            print("   ⚠️  Template package.json manquant")
            return

        # Lire le template
        template_content = template_path.read_text(encoding="utf-8")

        # Remplacer les placeholders
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

        # Nettoyer les virgules en trop
        template_content = template_content.replace(",\n    \n  }", "\n  }")
        template_content = template_content.replace(",\n    {{", "\n    {{")

        # Écrire le fichier
        (self.project_path / "package.json").write_text(
            template_content, encoding="utf-8"
        )
        print("   ✓ package.json")

    def create_project_files(self):
        """Crée les fichiers de base du projet selon le type."""
        print("\n📄 Création des fichiers de base...")

        # README.md
        readme_content = f"""# {self.project_name}

{self.PROJECT_TYPES[self.project_type]['description']}

## 🚀 Installation

```bash
npm install
```

## 🛠️ Développement

```bash
# Serveur de développement
npm run dev

# Build de production
npm run build

# Tests
npm test
npm run test:coverage

# Linting et formatage
npm run lint
npm run format
```

## 📋 Scripts Disponibles

- `npm run dev` - Serveur de développement
- `npm run build` - Build de production
- `npm run start` - Serveur de production
- `npm run lint` - Vérification ESLint
- `npm run format` - Formatage Prettier
- `npm test` - Tests Jest

## 📖 Documentation

Voir [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) pour le guide de développement complet.
"""
        (self.project_path / "README.md").write_text(readme_content, encoding="utf-8")
        print("   ✓ README.md")

        # Créer les fichiers selon le type
        self._create_type_specific_files()

        # TypeScript config (si nécessaire)
        if self.project_type != "vanilla":
            self._create_typescript_config()

        # Test example
        self._create_test_files()

    def _create_type_specific_files(self):
        """Crée les fichiers spécifiques au type de projet."""
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

        print(f"   ✓ Fichiers {self.project_type} créés")

    def _create_typescript_config(self):
        """Crée la configuration TypeScript."""
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
        """Crée les fichiers de test example."""
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
        print("\n🔧 Configuration VSCode...")

        vscode_files = ["settings.json", "extensions.json"]

        for file in vscode_files:
            source = self.js_tools_path / "vscode" / file
            dest = self.project_path / ".vscode" / file

            if source.exists():
                shutil.copy2(source, dest)
                print(f"   ✓ .vscode/{file}")
            else:
                print(f"   ⚠️  Fichier VSCode manquant: {file}")

    def install_dependencies(self):
        """Installe les dépendances NPM."""
        print("\n📦 Installation des dépendances...")

        try:
            # Vérifier npm
            subprocess.run(["npm", "--version"], capture_output=True, check=True)

            # Installer les dépendances
            print("   🔄 Installation en cours...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("   ✅ Dépendances installées")

                # Installer husky
                subprocess.run(
                    ["npx", "husky", "install"],
                    cwd=self.project_path,
                    capture_output=True,
                )
                print("   ✅ Hooks Husky configurés")
            else:
                print(f"   ⚠️  Erreur lors de l'installation: {result.stderr}")

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ⚠️  npm non trouvé. Installez Node.js/npm")

    def print_next_steps(self):
        """Affiche les prochaines étapes."""
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
    """Fonction principale."""
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
        project_name = input("Nom du projet JavaScript: ").strip()
        if not project_name:
            print("❌ Nom de projet requis")
            return 1
        project_path = Path.cwd() / project_name

    # Sélection du type si pas spécifié
    if not args.current_dir and not args.type:
        print("\n🎯 Quel type de projet JavaScript voulez-vous créer ?")
        for i, (key, config) in enumerate(
            JavaScriptProjectSetup.PROJECT_TYPES.items(), 1
        ):
            print(f"{i}. {key} - {config['description']}")

        try:
            choice = int(input("Choix (1-4): ")) - 1
            project_type = list(JavaScriptProjectSetup.PROJECT_TYPES.keys())[choice]
        except (ValueError, IndexError):
            project_type = "node"
    else:
        project_type = args.type

    # Confirmer avant de continuer
    if not args.current_dir:
        response = input(
            f"Créer le projet JavaScript '{project_name}' ({project_type}) dans {project_path}? (y/N): "
        )
        if response.lower() not in ("y", "yes", "o", "oui"):
            print("Annulé.")
            return 0

    setup = JavaScriptProjectSetup(project_path, project_name, project_type)
    setup.setup_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
