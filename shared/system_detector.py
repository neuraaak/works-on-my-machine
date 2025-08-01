#!/usr/bin/env python3
"""
Détecteur système avancé pour dev-tools.
Détecte OS, architecture, gestionnaires de paquets, et environnements de développement
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Importer le gestionnaire CLI
from shared.cli_manager import check_tool_available, run_silent


class SystemDetector:
    """Détecteur système complet."""

    def __init__(self):
        """Initialise le détecteur système."""
        self.system_info = self.get_system_info()
        self.package_managers = self.detect_package_managers()
        self.dev_environments = self.detect_development_environments()

    def get_system_info(self) -> Dict:
        """Retourne les informations système de base."""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "node": platform.node(),
            "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
            "home": str(Path.home()),
            "shell": os.environ.get("SHELL", "unknown"),
            "terminal": os.environ.get("TERM", "unknown"),
            "path_separator": os.pathsep,
            "line_separator": os.linesep,
        }

    def detect_package_managers(self) -> Dict[str, Dict]:
        """Détecte tous les gestionnaires de paquets disponibles."""
        managers = {}

        # Windows
        if self.system_info["platform"] == "Windows":
            managers.update(self._detect_windows_managers())

        # macOS
        elif self.system_info["platform"] == "Darwin":
            managers.update(self._detect_macos_managers())

        # Linux
        elif self.system_info["platform"] == "Linux":
            managers.update(self._detect_linux_managers())

        return managers

    def _detect_windows_managers(self) -> Dict[str, Dict]:
        """Détecte les gestionnaires Windows."""
        managers = {}

        # Chocolatey
        if check_tool_available("choco"):
            try:
                result = run_silent(["choco", "--version"])
                managers["chocolatey"] = {
                    "available": True,
                    "version": result.stdout.strip() if result.success else None,
                    "command": "choco",
                    "description": "Gestionnaire de paquets communautaire",
                    "install_cmd": "choco install",
                    "priority": 1,
                }
            except Exception:
                pass

        # Winget
        if check_tool_available("winget"):
            try:
                result = run_silent(["winget", "--version"])
                managers["winget"] = {
                    "available": True,
                    "version": result.stdout.strip() if result.success else None,
                    "command": "winget",
                    "description": "Gestionnaire Microsoft officiel",
                    "install_cmd": "winget install",
                    "priority": 2,
                }
            except Exception:
                pass

        # Scoop
        if check_tool_available("scoop"):
            try:
                result = run_silent(["scoop", "--version"])
                managers["scoop"] = {
                    "available": True,
                    "version": result.stdout.strip() if result.success else None,
                    "command": "scoop",
                    "description": "Gestionnaire pour développeurs",
                    "install_cmd": "scoop install",
                    "priority": 3,
                }
            except Exception:
                pass

        return managers

    def _detect_macos_managers(self) -> Dict[str, Dict]:
        """Détecte les gestionnaires macOS."""
        managers = {}

        # Homebrew
        if check_tool_available("brew"):
            try:
                result = run_silent(["brew", "--version"])
                version = result.stdout.split("\n")[0]
                managers["homebrew"] = {
                    "available": True,
                    "version": version,
                    "command": "brew",
                    "description": "Gestionnaire de paquets principal pour macOS",
                    "install_cmd": "brew install",
                    "priority": 1,
                }
            except Exception:
                pass

        # MacPorts
        if shutil.which("port"):
            try:
                result = run_silent(["port", "version"])
                managers["macports"] = {
                    "available": True,
                    "version": result.stdout.strip() if result.success else None,
                    "command": "port",
                    "description": "Gestionnaire de paquets alternatif",
                    "install_cmd": "sudo port install",
                    "priority": 2,
                }
            except Exception:
                pass

        return managers

    def _detect_linux_managers(self) -> Dict[str, Dict]:
        """Détecte les gestionnaires Linux."""
        managers = {}

        # APT (Debian/Ubuntu)
        if check_tool_available("apt"):
            try:
                result = run_silent(["apt", "--version"])
                managers["apt"] = {
                    "available": True,
                    "version": result.stdout.split("\n")[0],
                    "command": "apt",
                    "description": "Gestionnaire Debian/Ubuntu",
                    "install_cmd": "sudo apt install",
                    "priority": 1,
                }
            except Exception:
                pass

        # DNF (Fedora)
        if shutil.which("dnf"):
            try:
                result = run_silent(["dnf", "--version"])
                managers["dnf"] = {
                    "available": True,
                    "version": result.stdout.split("\n")[0],
                    "command": "dnf",
                    "description": "Gestionnaire Fedora/RHEL",
                    "install_cmd": "sudo dnf install",
                    "priority": 1,
                }
            except Exception:
                pass

        # YUM (CentOS/RHEL)
        if shutil.which("yum"):
            try:
                result = run_silent(["yum", "--version"])
                managers["yum"] = {
                    "available": True,
                    "version": result.stdout.split("\n")[0],
                    "command": "yum",
                    "description": "Gestionnaire CentOS/RHEL",
                    "install_cmd": "sudo yum install",
                    "priority": 2,
                }
            except Exception:
                pass

        # Pacman (Arch)
        if shutil.which("pacman"):
            try:
                result = run_silent(["pacman", "--version"])
                managers["pacman"] = {
                    "available": True,
                    "version": result.stdout.split("\n")[0],
                    "command": "pacman",
                    "description": "Gestionnaire Arch Linux",
                    "install_cmd": "sudo pacman -S",
                    "priority": 1,
                }
            except Exception:
                pass

        # Snap
        if shutil.which("snap"):
            try:
                result = run_silent(["snap", "--version"])
                managers["snap"] = {
                    "available": True,
                    "version": result.stdout.split("\n")[0],
                    "command": "snap",
                    "description": "Gestionnaire universel Ubuntu",
                    "install_cmd": "sudo snap install",
                    "priority": 3,
                }
            except Exception:
                pass

        return managers

    def detect_development_environments(self) -> Dict[str, Dict]:
        """Détecte les environnements de développement."""
        envs = {}

        # Éditeurs/IDEs
        editors = {
            "code": "Visual Studio Code",
            "code-insiders": "VS Code Insiders",
            "subl": "Sublime Text",
            "atom": "Atom",
            "vim": "Vim",
            "nvim": "Neovim",
            "emacs": "Emacs",
            "nano": "Nano",
        }

        for cmd, name in editors.items():
            if shutil.which(cmd):
                try:
                    result = run_silent([cmd, "--version"])
                    envs[cmd] = {
                        "available": True,
                        "name": name,
                        "version": (
                            result.stdout.split("\n")[0] if result.stdout else "unknown"
                        ),
                        "command": cmd,
                    }
                except Exception:
                    envs[cmd] = {
                        "available": True,
                        "name": name,
                        "version": "unknown",
                        "command": cmd,
                    }

        # Shells
        shells = {
            "bash": "Bash",
            "zsh": "Zsh",
            "fish": "Fish",
            "powershell": "PowerShell",
            "pwsh": "PowerShell Core",
        }

        for cmd, name in shells.items():
            if shutil.which(cmd):
                envs[f"shell_{cmd}"] = {
                    "available": True,
                    "name": name,
                    "command": cmd,
                    "type": "shell",
                }

        return envs

    def get_best_package_manager(self) -> Optional[str]:
        """Retourne le meilleur gestionnaire disponible."""
        available = {
            name: info
            for name, info in self.package_managers.items()
            if info["available"]
        }

        if not available:
            return None

        # Trier par priorité
        sorted_managers = sorted(available.items(), key=lambda x: x[1]["priority"])
        return sorted_managers[0][0]

    def can_install_package_manager(self) -> Optional[str]:
        """Vérifie si on peut installer un gestionnaire de paquets."""
        if self.system_info["platform"] == "Windows":
            # Peut installer Chocolatey via PowerShell
            if shutil.which("powershell") or shutil.which("pwsh"):
                return "chocolatey"
        elif self.system_info["platform"] == "Darwin":
            # Peut installer Homebrew via curl
            if shutil.which("curl"):
                return "homebrew"

        return None

    def export_report(self, output_path: Optional[Path] = None) -> Path:
        """Génère et exporte un rapport détaillé du système."""
        report = {
            "system_info": self.system_info,
            "package_managers": self.package_managers,
            "development_environments": self.dev_environments,
            "recommendations": self.get_recommendations(),
        }

        if output_path is None:
            output_path = Path.cwd() / "system_report.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return output_path

    def get_recommendations(self) -> Dict[str, str]:
        """Génère des recommandations basées sur la détection."""
        recommendations = {}

        # Gestionnaire de paquets
        best_manager = self.get_best_package_manager()
        if best_manager:
            recommendations["package_manager"] = (
                f"Utiliser {best_manager} pour les installations"
            )
        else:
            installable = self.can_install_package_manager()
            if installable:
                recommendations["package_manager"] = (
                    f"Installer {installable} pour faciliter les installations"
                )
            else:
                recommendations["package_manager"] = (
                    "Aucun gestionnaire de paquets détecté - installation manuelle requise"
                )

        # Éditeur recommandé
        if "code" in self.dev_environments:
            recommendations["editor"] = (
                "VS Code détecté - excellent choix pour dev-tools"
            )
        elif any("vim" in env or "nvim" in env for env in self.dev_environments):
            recommendations["editor"] = (
                "Éditeur en ligne de commande détecté - dev-tools compatible"
            )
        else:
            recommendations["editor"] = (
                "Installer VS Code recommandé pour une meilleure intégration"
            )

        return recommendations

    def print_summary(self):
        """Affiche un résumé système."""
        print("🖥️  Informations Système")
        print("=" * 40)
        print(
            f"OS: {self.system_info['platform']} {self.system_info['platform_release']}"
        )
        print(f"Architecture: {self.system_info['architecture']}")
        print(f"Python: {self.system_info['python_version']}")
        print(f"Shell: {self.system_info['shell']}")

        print(
            f"\n📦 Gestionnaires de Paquets ({len(self.package_managers)} disponibles)"
        )
        print("-" * 50)
        for name, info in self.package_managers.items():
            if info["available"]:
                print(f"✅ {name}: {info['version']} - {info['description']}")

        print(
            f"\n🛠️  Environnements de Développement ({len(self.dev_environments)} détectés)"
        )
        print("-" * 60)
        for _, info in self.dev_environments.items():
            if info["available"]:
                print(f"✅ {info['name']}: {info.get('version', 'unknown')}")

        print("\n💡 Recommandations")
        print("-" * 20)
        for category, recommendation in self.get_recommendations().items():
            print(f"• {category}: {recommendation}")


def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Détecteur système pour dev-tools")
    parser.add_argument("--export", help="Exporter le rapport vers un fichier JSON")
    parser.add_argument("--summary", action="store_true", help="Afficher un résumé")

    args = parser.parse_args()

    detector = SystemDetector()

    if args.export:
        output_path = detector.export_report(Path(args.export))
        print(f"📄 Rapport exporté vers: {output_path}")

    if args.summary or not args.export:
        detector.print_summary()


if __name__ == "__main__":
    main()
