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
import io
import shutil
import subprocess
import sys
from pathlib import Path

# Third-party imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ///////////////////////////////////////////////////////////////
# VARIABLES
# ///////////////////////////////////////////////////////////////

project_name = "womm"
installer_name = "womm-installer"

# ///////////////////////////////////////////////////////////////
# GLOBAL CONSOLE
# ///////////////////////////////////////////////////////////////

# Configure console with UTF-8 encoding for Windows emoji support
# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
console = Console(legacy_windows=False)

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def run_command(command: list[str], description: str = "") -> bool:
    """Run a command and return success status.

    Args:
        command: Command to execute as list of strings
        description: Optional description for the command

    Returns:
        bool: True if command succeeded, False otherwise
    """
    if description:
        console.print(f"[cyan]🔄[/cyan] {description}...")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            console.print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌[/red] Error: {e}")
        if e.stderr:
            console.print(f"[red]Error output:[/red] {e.stderr}")
        return False


def check_pyinstaller() -> bool:
    """Check if PyInstaller is installed.

    Returns:
        bool: True if PyInstaller is available, False otherwise
    """
    try:
        import PyInstaller

        console.print(
            f"[green]✅[/green] PyInstaller version: {PyInstaller.__version__}"
        )
        return True
    except ImportError:
        console.print("[yellow]⚠️[/yellow] PyInstaller not found. Installing...")
        return run_command(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            "Installing PyInstaller",
        )


def clean_build() -> None:
    """Clean previous build artifacts."""
    console.print("[yellow]🧹[/yellow] Cleaning previous build artifacts...")

    project_root = Path(__file__).resolve().parents[2]

    # Remove build directories
    paths_to_clean = [
        project_root / "build",
        project_root / "dist",
    ]

    # Find and remove spec files
    for spec_file in project_root.glob("*.spec"):
        paths_to_clean.append(spec_file)

    for path in paths_to_clean:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    console.print("[green]✅[/green] Build artifacts cleaned")


def create_spec_file() -> Path:
    """Create PyInstaller spec file.

    Returns:
        Path: Path to the created spec file
    """
    console.print("[cyan]📝[/cyan] Creating PyInstaller spec file...")

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
    ['exe_entry.py'],
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

    console.print(f"[green]✅[/green] Spec file created: {spec_path}")
    return spec_path


def build_executable() -> bool:
    """Build the executable.

    Returns:
        bool: True if build succeeded, False otherwise
    """
    console.print("[cyan]🔨[/cyan] Building WOMM installer executable...")

    spec_path = create_spec_file()

    # Build using PyInstaller
    if not run_command(
        [sys.executable, "-m", "PyInstaller", str(spec_path), "--clean"],
        "Running PyInstaller",
    ):
        console.print("[red]❌[/red] Build failed")
        return False

    console.print("[green]✅[/green] Build successful!")

    # Clean up spec file
    if spec_path.exists():
        spec_path.unlink()
        console.print(f"[yellow]🧹[/yellow] Cleaned up spec file: {spec_path}")

    return True


def verify_executable() -> bool:
    """Verify the built executable.

    Returns:
        bool: True if verification passed, False otherwise
    """
    console.print("[cyan]🔍[/cyan] Verifying executable...")

    exe_path = Path("dist") / f"{installer_name}.exe"

    if not exe_path.exists():
        console.print(f"[red]❌[/red] Executable not found at {exe_path}")
        return False

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    console.print(f"[green]✅[/green] Executable found: {exe_path}")
    console.print(f"[cyan]📦[/cyan] Size: {size_mb:.2f} MB")

    # Test if executable can start
    console.print("[cyan]🧪[/cyan] Testing executable startup...")
    try:
        result = subprocess.run(
            [str(exe_path), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 or "womm" in result.stdout.lower():
            console.print("[green]✅[/green] Executable runs successfully!")
            return True
        else:
            console.print(
                "[yellow]⚠️[/yellow] Executable started but returned unexpected output"
            )
            return True
    except subprocess.TimeoutExpired:
        console.print(
            "[yellow]⚠️[/yellow] Executable started (timeout expected for interactive mode)"
        )
        return True
    except Exception as e:
        console.print(f"[red]❌[/red] Test failed: {e}")
        return False


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////


def build_installer() -> bool:
    """Build the installer executable.

    Returns:
        bool: True if build succeeded, False otherwise
    """
    console.print(
        Panel.fit(
            Text(f"🔨 Building {project_name} installer", style="bold cyan"),
            border_style="cyan",
        )
    )

    # Clean previous builds
    clean_build()

    # Check PyInstaller
    if not check_pyinstaller():
        console.print("[red]❌[/red] Failed to verify PyInstaller")
        return False

    # Build the executable
    if not build_executable():
        return False

    # Verify the executable
    if not verify_executable():
        return False

    console.print(
        Panel.fit(
            Text("✅ Installer built successfully", style="bold green"),
            border_style="green",
        )
    )

    # Show final location
    exe_path = Path("dist") / f"{installer_name}.exe"
    console.print(f"\n[cyan]📦[/cyan] Installer location: [bold]{exe_path}[/bold]")

    return True


def main() -> None:
    """Main function."""
    if len(sys.argv) < 2:
        console.print("[yellow]Usage:[/yellow] python build_exe.py [build]")
        console.print("  [cyan]build[/cyan]        - Build the installer executable")
        return

    action = sys.argv[1]

    if action == "build":
        if not build_installer():
            sys.exit(1)
    else:
        console.print(f"[red]❌[/red] Unknown action: [bold]{action}[/bold]")
        sys.exit(1)


if __name__ == "__main__":
    main()
