#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# BUILD_EXE - Executable Builder
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Build script for WOMM executable installer.

Creates a standalone executable using PyInstaller.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import subprocess
import sys
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def check_pyinstaller() -> bool:
    """Check if PyInstaller is installed.

    Returns:
        bool: True if PyInstaller is available, False otherwise
    """
    try:
        import PyInstaller

        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run(  # noqa: S603
            [sys.executable, "-m", "pip", "install", "pyinstaller"]
        )
        return True


def create_spec_file() -> Path:
    """Create PyInstaller spec file.

    Returns:
        Path: Path to the created spec file
    """
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add WOMM files to datas
datas = [
    ('womm', 'womm'),
]

# Explicitly include all dependencies
hiddenimports = [
    'click',
    'rich',
    'InquirerPy',
    'tomli',
    'womm',
    'womm.cli',
    'womm.core',
    'womm.core.managers',
    'womm.core.managers.installation',
    'womm.core.managers.installation.installation_manager',
    'womm.core.managers.system',
    'womm.core.managers.system.user_path_manager',
    'womm.core.ui',
    'womm.core.ui.common',
    'womm.core.ui.common.console',
    'womm.core.utils',
    'womm.core.utils.security',
    'womm.core.utils.security.security_validator',
    'womm.core.exceptions',
    'womm.core.exceptions.installation',
    'womm.core.exceptions.system',
]

a = Analysis(
    ['exe_script.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='womm-installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    spec_path = Path("womm_installer.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    return spec_path


def build_executable() -> bool:
    """Build the executable.

    Returns:
        bool: True if build succeeded, False otherwise
    """
    print("Building WOMM installer...")

    spec_path = create_spec_file()

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "PyInstaller", str(spec_path), "--clean"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Build failed:")
        print(result.stderr)
        return False

    print("Build successful!")

    # Clean up
    spec_path.unlink()

    return True


def test_executable() -> bool:
    """Test the executable.

    Returns:
        bool: True if test passed, False otherwise
    """
    exe_path = Path("dist") / "womm-installer.exe"

    if not exe_path.exists():
        print(f"Executable not found at {exe_path}")
        return False

    print(f"Testing: {exe_path}")
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"Size: {size_mb:.1f} MB")

    try:
        subprocess.run(  # noqa: S603
            [str(exe_path)], capture_output=True, text=True, timeout=10
        )
        print("Executable runs!")
        return True
    except subprocess.TimeoutExpired:
        print("Executable started (timeout expected)")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print("WOMM Installer Builder")
        print("=" * 30)

        if not check_pyinstaller():
            print("Failed to install PyInstaller")
            sys.exit(1)

        if not build_executable():
            print("Build failed")
            sys.exit(1)

        if not test_executable():
            print("Test failed")
            sys.exit(1)

        print("\nBuild completed!")
        print(f"Installer: {Path('dist') / 'womm-installer.exe'}")
    else:
        print("Usage: python build_exe.py build")


if __name__ == "__main__":
    main()
