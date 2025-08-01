#!/usr/bin/env python3
"""
Security test script for Works On My Machine.
Tests all security validations and ensures they work correctly.
"""

import sys
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from shared.security_validator import SecurityValidator, validate_user_input
from shared.secure_cli_manager import run_secure_command


def test_project_name_validation():
    """Test project name validation."""
    print("🧪 Testing project name validation...")
    
    validator = SecurityValidator()
    
    # Tests valides
    valid_names = [
        "my-project",
        "my_project",
        "myproject",
        "MyProject",
        "project123",
        "a" * 50,  # Longueur maximale
    ]
    
    for name in valid_names:
        is_valid, error = validator.validate_project_name(name)
        if not is_valid:
            print(f"❌ Valid name rejected: {name} - {error}")
            return False
        else:
            print(f"✅ Valid name accepted: {name}")
    
    # Tests invalides
    invalid_names = [
        "",  # Vide
        "a" * 51,  # Trop long
        "my;project",  # Caractère dangereux
        "my..project",  # Path traversal
        "my<project",  # Redirection
        "con",  # Nom réservé Windows
        "prn",  # Nom réservé Windows
        "my project",  # Espace
        "my/project",  # Slash
        "my\\project",  # Backslash
    ]
    
    for name in invalid_names:
        is_valid, error = validator.validate_project_name(name)
        if is_valid:
            print(f"❌ Invalid name accepted: {name}")
            return False
        else:
            print(f"✅ Invalid name rejected: {name} - {error}")
    
    return True


def test_path_validation():
    """Test path validation."""
    print("\n🧪 Testing path validation...")
    
    validator = SecurityValidator()
    
    # Tests valides
    valid_paths = [
        "/home/user/project",
        "C:\\Users\\user\\project",
        "./relative/path",
        "project",
    ]
    
    for path in valid_paths:
        is_valid, error = validator.validate_path(path)
        if not is_valid:
            print(f"❌ Valid path rejected: {path} - {error}")
            return False
        else:
            print(f"✅ Valid path accepted: {path}")
    
    # Tests invalides
    invalid_paths = [
        "path/../dangerous",  # Path traversal
        "path\\..\\dangerous",  # Path traversal Windows
        "path;dangerous",  # Caractère dangereux
        "path|dangerous",  # Caractère dangereux
        "path`dangerous",  # Caractère dangereux
        "path$(dangerous)",  # Caractère dangereux
        "path<dangerous",  # Redirection
        "path>dangerous",  # Redirection
    ]
    
    for path in invalid_paths:
        is_valid, error = validator.validate_path(path)
        if is_valid:
            print(f"❌ Invalid path accepted: {path}")
            return False
        else:
            print(f"✅ Invalid path rejected: {path} - {error}")
    
    return True


def test_command_validation():
    """Test command validation."""
    print("\n🧪 Testing command validation...")
    
    validator = SecurityValidator()
    
    # Tests valides
    valid_commands = [
        ["python", "--version"],
        ["git", "status"],
        ["npm", "install"],
        ["black", "src/"],
        ["flake8", "project"],
    ]
    
    for cmd in valid_commands:
        is_valid, error = validator.validate_command(cmd)
        if not is_valid:
            print(f"❌ Valid command rejected: {cmd} - {error}")
            return False
        else:
            print(f"✅ Valid command accepted: {cmd}")
    
    # Tests invalides
    invalid_commands = [
        ["rm", "-rf", "/"],  # Commande dangereuse
        ["sudo", "rm", "-rf", "/"],  # Commande dangereuse
        ["python", ";", "rm", "-rf", "/"],  # Injection
        ["python", "&&", "rm", "-rf", "/"],  # Injection
        ["python", "|", "rm", "-rf", "/"],  # Injection
        ["python", "`rm -rf /`"],  # Injection
        ["python", "$(rm -rf /)"],  # Injection
    ]
    
    for cmd in invalid_commands:
        is_valid, error = validator.validate_command(cmd)
        if is_valid:
            print(f"❌ Invalid command accepted: {cmd}")
            return False
        else:
            print(f"✅ Invalid command rejected: {cmd} - {error}")
    
    return True


def test_script_execution_validation():
    """Test script execution validation."""
    print("\n🧪 Testing script execution validation...")
    
    validator = SecurityValidator()
    
    # Test avec un script valide
    valid_script = Path(__file__).parent / "shared" / "security_validator.py"
    is_valid, error = validator.validate_script_execution(valid_script)
    if not is_valid:
        print(f"❌ Valid script rejected: {valid_script} - {error}")
        return False
    else:
        print(f"✅ Valid script accepted: {valid_script}")
    
    # Test avec un script inexistant
    invalid_script = Path(__file__).parent / "nonexistent.py"
    is_valid, error = validator.validate_script_execution(invalid_script)
    if is_valid:
        print(f"❌ Invalid script accepted: {invalid_script}")
        return False
    else:
        print(f"✅ Invalid script rejected: {invalid_script} - {error}")
    
    return True


def test_secure_command_execution():
    """Test secure command execution."""
    print("\n🧪 Testing secure command execution...")
    
    # Test avec une commande valide
    result = run_secure_command(["python", "--version"], "Testing Python version")
    if result.success and result.security_validated:
        print(f"✅ Secure command executed successfully: {result}")
    else:
        print(f"❌ Secure command failed: {result}")
        return False
    
    # Test avec une commande invalide
    result = run_secure_command(["invalid_command"], "Testing invalid command")
    if not result.success:
        print(f"✅ Invalid command correctly rejected: {result}")
    else:
        print(f"❌ Invalid command incorrectly accepted: {result}")
        return False
    
    return True


def test_user_input_validation():
    """Test user input validation."""
    print("\n🧪 Testing user input validation...")
    
    # Test project name validation
    is_valid, error = validate_user_input("my-project", "project_name")
    if not is_valid:
        print(f"❌ Valid project name rejected: {error}")
        return False
    else:
        print("✅ Valid project name accepted")
    
    # Test invalid project name
    is_valid, error = validate_user_input("my;project", "project_name")
    if is_valid:
        print("❌ Invalid project name accepted")
        return False
    else:
        print(f"✅ Invalid project name rejected: {error}")
    
    # Test path validation
    is_valid, error = validate_user_input("/home/user/project", "path")
    if not is_valid:
        print(f"❌ Valid path rejected: {error}")
        return False
    else:
        print("✅ Valid path accepted")
    
    # Test invalid path
    is_valid, error = validate_user_input("path/../dangerous", "path")
    if is_valid:
        print("❌ Invalid path accepted")
        return False
    else:
        print(f"✅ Invalid path rejected: {error}")
    
    return True


def main():
    """Run all security tests."""
    print("🔒 Security Test Suite for Works On My Machine")
    print("=" * 50)
    
    tests = [
        test_project_name_validation,
        test_path_validation,
        test_command_validation,
        test_script_execution_validation,
        test_secure_command_execution,
        test_user_input_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All security tests passed!")
        return 0
    else:
        print("⚠️  Some security tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())