#!/usr/bin/env python3
"""
Migration script for Works On My Machine security improvements.
This script helps migrate from the original CLI to the secure version.
"""

import os
import shutil
import sys
from pathlib import Path


def backup_original_files():
    """Create backup of original files."""
    print("📦 Creating backup of original files...")
    
    backup_dir = Path(".backup_original")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "wom.py",
        "shared/cli_manager.py",
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_path = backup_dir / Path(file_path).name
            shutil.copy2(file_path, backup_path)
            print(f"   ✓ Backed up: {file_path} -> {backup_path}")
    
    print(f"✅ Backup completed in {backup_dir}")


def install_secure_modules():
    """Install secure modules."""
    print("\n🔒 Installing secure modules...")
    
    # Vérifier que les nouveaux modules existent
    required_files = [
        "shared/security_validator.py",
        "shared/secure_cli_manager.py",
        "wom_secure.py",
        "test_security.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure all security modules are present before migration.")
        return False
    
    print("   ✓ All secure modules found")
    return True


def replace_cli_manager():
    """Replace CLI manager with secure version."""
    print("\n🔄 Replacing CLI manager...")
    
    try:
        # Créer une sauvegarde du gestionnaire original
        original_manager = Path("shared/cli_manager.py")
        backup_manager = Path("shared/cli_manager_original.py")
        
        if original_manager.exists():
            shutil.copy2(original_manager, backup_manager)
            print(f"   ✓ Backed up: {original_manager} -> {backup_manager}")
        
        # Copier le gestionnaire sécurisé
        secure_manager = Path("shared/secure_cli_manager.py")
        shutil.copy2(secure_manager, original_manager)
        print(f"   ✓ Replaced: {original_manager} with secure version")
        
        return True
    except Exception as e:
        print(f"❌ Error replacing CLI manager: {e}")
        return False


def update_wom_py():
    """Update wom.py with secure version."""
    print("\n🔄 Updating wom.py...")
    
    try:
        # Créer une sauvegarde
        original_wom = Path("wom.py")
        backup_wom = Path("wom_original.py")
        
        if original_wom.exists():
            shutil.copy2(original_wom, backup_wom)
            print(f"   ✓ Backed up: {original_wom} -> {backup_wom}")
        
        # Copier la version sécurisée
        secure_wom = Path("wom_secure.py")
        shutil.copy2(secure_wom, original_wom)
        print(f"   ✓ Replaced: {original_wom} with secure version")
        
        return True
    except Exception as e:
        print(f"❌ Error updating wom.py: {e}")
        return False


def update_imports():
    """Update imports in existing scripts to use secure modules."""
    print("\n📝 Updating imports...")
    
    # Scripts à mettre à jour
    scripts_to_update = [
        "init.py",
        "lint.py",
        "shared/prerequisite_installer.py",
        "shared/deploy-devtools.py",
        "shared/cspell_manager.py",
        "shared/environment_manager.py",
        "shared/project_detector.py",
        "shared/system_detector.py",
        "shared/vscode_config.py",
    ]
    
    updated_count = 0
    for script_path in scripts_to_update:
        if Path(script_path).exists():
            if update_script_imports(script_path):
                updated_count += 1
                print(f"   ✓ Updated: {script_path}")
            else:
                print(f"   ⚠️  No changes needed: {script_path}")
    
    print(f"✅ Updated {updated_count} scripts")


def update_script_imports(script_path):
    """Update imports in a specific script."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remplacer les imports du gestionnaire CLI
        replacements = [
            ("from shared.cli_manager import", "from shared.secure_cli_manager import"),
            ("import shared.cli_manager", "import shared.secure_cli_manager"),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Si le contenu a changé, écrire le fichier
        if content != original_content:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"   ❌ Error updating {script_path}: {e}")
        return False


def run_security_tests():
    """Run security tests to verify the migration."""
    print("\n🧪 Running security tests...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_security.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Security tests passed")
            return True
        else:
            print("❌ Security tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running security tests: {e}")
        return False


def create_migration_report():
    """Create a migration report."""
    print("\n📋 Creating migration report...")
    
    report_content = f"""# Migration Report - Works On My Machine Security

## Migration Date
{Path().cwd()}

## Files Modified
- wom.py -> wom_secure.py
- shared/cli_manager.py -> shared/secure_cli_manager.py
- Updated imports in {len([s for s in [
        "init.py", "lint.py", "shared/prerequisite_installer.py",
        "shared/deploy-devtools.py", "shared/cspell_manager.py",
        "shared/environment_manager.py", "shared/project_detector.py",
        "shared/system_detector.py", "shared/vscode_config.py"
    ] if Path(s).exists()])} scripts

## Backups Created
- .backup_original/ (original files)
- wom_original.py
- shared/cli_manager_original.py

## Security Improvements
✅ Input validation for all user inputs
✅ Command injection protection
✅ Path traversal protection
✅ Secure script execution
✅ Enhanced error handling
✅ Security logging
✅ Automated retry with timeout

## Next Steps
1. Test the secure CLI: python wom.py --help
2. Run security tests: python test_security.py
3. Update documentation if needed
4. Monitor for any issues

## Rollback Instructions
To rollback to the original version:
1. Restore wom.py from wom_original.py
2. Restore shared/cli_manager.py from shared/cli_manager_original.py
3. Restore other files from .backup_original/

## Support
If you encounter issues, check the security logs and run the test suite.
"""
    
    with open("MIGRATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("✅ Migration report created: MIGRATION_REPORT.md")


def main():
    """Main migration function."""
    print("🔄 Works On My Machine - Security Migration")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("wom.py").exists():
        print("❌ Error: wom.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Étapes de migration
    steps = [
        ("Creating backups", backup_original_files),
        ("Installing secure modules", install_secure_modules),
        ("Replacing CLI manager", replace_cli_manager),
        ("Updating wom.py", update_wom_py),
        ("Updating imports", update_imports),
        ("Running security tests", run_security_tests),
        ("Creating migration report", create_migration_report),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            if step_func():
                success_count += 1
                print(f"✅ {step_name} completed")
            else:
                print(f"❌ {step_name} failed")
        except Exception as e:
            print(f"❌ {step_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Migration Results: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the secure CLI: python wom.py --help")
        print("2. Run security tests: python test_security.py")
        print("3. Check the migration report: MIGRATION_REPORT.md")
        return 0
    else:
        print("⚠️  Migration partially completed. Check the errors above.")
        print("\n🔄 To retry, run this script again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())