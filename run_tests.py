#!/usr/bin/env python3
"""
Script de lancement des tests pour Works On My Machine.
Fournit différentes options pour exécuter les tests selon les besoins.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Exécute une commande et affiche le résultat."""
    print(f"\n🔍 {description}...")
    print(f"Commande: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Succès")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec (code: {e.returncode})")
        if e.stdout:
            print("Sortie standard:")
            print(e.stdout)
        if e.stderr:
            print("Erreur:")
            print(e.stderr)
        return False


def run_unit_tests():
    """Lance les tests unitaires."""
    cmd = [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"]
    return run_command(cmd, "Lancement des tests unitaires")


def run_integration_tests():
    """Lance les tests d'intégration."""
    cmd = [sys.executable, "-m", "pytest", "tests/integration/", "-v", "--tb=short"]
    return run_command(cmd, "Lancement des tests d'intégration")


def run_security_tests():
    """Lance les tests de sécurité."""
    cmd = [sys.executable, "-m", "pytest", "-m", "security", "-v", "--tb=short"]
    return run_command(cmd, "Lancement des tests de sécurité")


def run_all_tests():
    """Lance tous les tests."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    return run_command(cmd, "Lancement de tous les tests")


def run_tests_with_coverage():
    """Lance les tests avec couverture de code."""
    cmd = [
        sys.executable, "-m", "pytest", "tests/", 
        "--cov=shared", "--cov=languages", "--cov-report=html", "--cov-report=term",
        "-v", "--tb=short"
    ]
    return run_command(cmd, "Lancement des tests avec couverture")


def run_fast_tests():
    """Lance les tests rapides (exclut les tests lents)."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-m", "not slow", "-v", "--tb=short"]
    return run_command(cmd, "Lancement des tests rapides")


def run_specific_test(test_path):
    """Lance un test spécifique."""
    cmd = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]
    return run_command(cmd, f"Lancement du test spécifique: {test_path}")


def run_tests_with_parallel():
    """Lance les tests en parallèle."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-n", "auto", "-v", "--tb=short"]
    return run_command(cmd, "Lancement des tests en parallèle")


def run_tests_with_debug():
    """Lance les tests en mode debug."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=long", "-s"]
    return run_command(cmd, "Lancement des tests en mode debug")


def check_test_dependencies():
    """Vérifie les dépendances de test."""
    print("🔍 Vérification des dépendances de test...")
    
    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-xdist"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True


def show_test_summary():
    """Affiche un résumé des tests disponibles."""
    print("📋 Résumé des tests disponibles:")
    print()
    
    test_categories = [
        ("Tests unitaires", "tests/unit/", "Tests des composants individuels"),
        ("Tests d'intégration", "tests/integration/", "Tests des interactions entre composants"),
        ("Tests de sécurité", "tests/unit/test_security_*.py", "Tests des validations de sécurité"),
        ("Tests CLI", "tests/unit/test_wom_cli.py", "Tests de l'interface en ligne de commande"),
    ]
    
    for category, path, description in test_categories:
        test_path = Path(path)
        if test_path.exists():
            test_files = list(test_path.glob("test_*.py"))
            print(f"🔹 {category}: {len(test_files)} fichiers de test")
            print(f"   📁 {path}")
            print(f"   📝 {description}")
            print()


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Script de lancement des tests pour Works On My Machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python run_tests.py --unit                    # Tests unitaires uniquement
  python run_tests.py --integration             # Tests d'intégration uniquement
  python run_tests.py --security                # Tests de sécurité uniquement
  python run_tests.py --all                     # Tous les tests
  python run_tests.py --coverage                # Tests avec couverture
  python run_tests.py --fast                    # Tests rapides (sans tests lents)
  python run_tests.py --parallel                # Tests en parallèle
  python run_tests.py --debug                   # Tests en mode debug
  python run_tests.py --check-deps              # Vérifier les dépendances
  python run_tests.py --summary                 # Afficher le résumé
  python run_tests.py tests/unit/test_security_validator.py  # Test spécifique
        """
    )
    
    parser.add_argument(
        "--unit", action="store_true",
        help="Lancer les tests unitaires uniquement"
    )
    parser.add_argument(
        "--integration", action="store_true",
        help="Lancer les tests d'intégration uniquement"
    )
    parser.add_argument(
        "--security", action="store_true",
        help="Lancer les tests de sécurité uniquement"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Lancer tous les tests"
    )
    parser.add_argument(
        "--coverage", action="store_true",
        help="Lancer les tests avec couverture de code"
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Lancer les tests rapides (exclut les tests lents)"
    )
    parser.add_argument(
        "--parallel", action="store_true",
        help="Lancer les tests en parallèle"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Lancer les tests en mode debug"
    )
    parser.add_argument(
        "--check-deps", action="store_true",
        help="Vérifier les dépendances de test"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Afficher le résumé des tests disponibles"
    )
    parser.add_argument(
        "test_path", nargs="?", default=None,
        help="Chemin vers un test spécifique"
    )
    
    args = parser.parse_args()
    
    # Afficher le résumé si demandé
    if args.summary:
        show_test_summary()
        return
    
    # Vérifier les dépendances si demandé
    if args.check_deps:
        check_test_dependencies()
        return
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("tests").exists():
        print("❌ Erreur: Répertoire 'tests' non trouvé.")
        print("Assurez-vous d'exécuter ce script depuis la racine du projet.")
        sys.exit(1)
    
    # Exécuter les tests selon les arguments
    success = True
    
    if args.test_path:
        success = run_specific_test(args.test_path)
    elif args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.security:
        success = run_security_tests()
    elif args.coverage:
        success = run_tests_with_coverage()
    elif args.fast:
        success = run_fast_tests()
    elif args.parallel:
        success = run_tests_with_parallel()
    elif args.debug:
        success = run_tests_with_debug()
    elif args.all:
        success = run_all_tests()
    else:
        # Par défaut, lancer tous les tests
        print("🚀 Lancement de tous les tests (par défaut)")
        success = run_all_tests()
    
    # Afficher le résultat final
    if success:
        print("\n🎉 Tous les tests ont réussi !")
        sys.exit(0)
    else:
        print("\n❌ Certains tests ont échoué.")
        sys.exit(1)


if __name__ == "__main__":
    main()