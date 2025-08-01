#!/usr/bin/env python3
"""
Works On My Machine (WOM) - Secure CLI Entry Point
Universal development tools for Python and JavaScript projects.
Enhanced with comprehensive security validation.
"""

import platform
import sys
from pathlib import Path

import click

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from shared.secure_cli_manager import run_secure_command
from shared.security_validator import validate_user_input, security_validator


@click.group()
@click.version_option(version="1.0.0")
def wom():
    """🛠️ Works On My Machine - Universal development tools.
    
    Automatic installation, cross-platform configuration, global commands
    for Python and JavaScript projects.
    
    🔒 Enhanced with comprehensive security validation.
    """
    pass


@wom.group()
def new():
    """🆕 Create new projects."""
    pass


@new.command("python")
@click.argument("project_name", required=False)
@click.option("--current-dir", is_flag=True, help="Configure current directory instead of creating new one")
def new_python(project_name, current_dir):
    """Create a new Python project with full development environment."""
    # Validation de sécurité
    if project_name:
        is_valid, error = validate_user_input(project_name, 'project_name')
        if not is_valid:
            click.echo(f"❌ Invalid project name: {error}", err=True)
            sys.exit(1)
    
    script_path = Path(__file__).parent / "languages" / "python" / "scripts" / "setup_project.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)
    
    result = run_secure_command(cmd, "Setting up Python project")
    sys.exit(0 if result.success and result.security_validated else 1)


@new.command("javascript")
@click.argument("project_name", required=False)
@click.option("--current-dir", is_flag=True, help="Configure current directory instead of creating new one")
@click.option("--type", "project_type", type=click.Choice(["node", "react", "vue", "express"]), 
    default="node", help="JavaScript project type")
def new_javascript(project_name, current_dir, project_type):
    """Create a new JavaScript/Node.js project with development tools."""
    # Validation de sécurité
    if project_name:
        is_valid, error = validate_user_input(project_name, 'project_name')
        if not is_valid:
            click.echo(f"❌ Invalid project name: {error}", err=True)
            sys.exit(1)
    
    script_path = Path(__file__).parent / "languages" / "javascript" / "scripts" / "setup_project.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)
    
    cmd.extend(["--type", project_type])
    
    result = run_secure_command(cmd, f"Setting up {project_type} project")
    sys.exit(0 if result.success and result.security_validated else 1)


@new.command("detect")
@click.argument("project_name", required=False)
@click.option("--current-dir", is_flag=True, help="Configure current directory")
def new_detect(project_name, current_dir):
    """Auto-detect project type and create appropriate setup."""
    # Validation de sécurité
    if project_name:
        is_valid, error = validate_user_input(project_name, 'project_name')
        if not is_valid:
            click.echo(f"❌ Invalid project name: {error}", err=True)
            sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "project_detector.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)
    
    result = run_secure_command(cmd, "Auto-detecting and setting up project")
    sys.exit(0 if result.success and result.security_validated else 1)


@wom.group()
def lint():
    """🎨 Code quality and linting tools."""
    pass


@lint.command("python")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_python(path, fix):
    """Lint Python code with flake8, black, and isort."""
    # Validation du chemin
    is_valid, error = validate_user_input(str(path), 'path')
    if not is_valid:
        click.echo(f"❌ Invalid path: {error}", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "languages" / "python" / "scripts" / "lint.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), str(path)]
    if fix:
        cmd.append("--fix")
    
    result = run_secure_command(cmd, f"Linting Python code in {path}")
    sys.exit(0 if result.success and result.security_validated else 1)


@lint.command("all")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_all(path, fix):
    """Lint all supported code in project."""
    # Validation du chemin
    is_valid, error = validate_user_input(str(path), 'path')
    if not is_valid:
        click.echo(f"❌ Invalid path: {error}", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "lint.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), str(path)]
    if fix:
        cmd.append("--fix")
    
    result = run_secure_command(cmd, f"Linting all code in {path}")
    sys.exit(0 if result.success and result.security_validated else 1)


@wom.group()
def spell():
    """📝 Spell checking with CSpell."""
    pass


@spell.command("install")
def spell_install():
    """Install CSpell and dictionaries globally."""
    script_path = Path(__file__).parent / "shared" / "cspell_manager.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), "--install"]
    result = run_secure_command(cmd, "Installing CSpell globally")
    sys.exit(0 if result.success and result.security_validated else 1)


@spell.command("setup")
@click.argument("project_name")
@click.option("--type", "project_type", type=click.Choice(["python", "javascript"]), 
              help="Force project type")
def spell_setup(project_name, project_type):
    """Setup CSpell for current project."""
    # Validation du nom de projet
    is_valid, error = validate_user_input(project_name, 'project_name')
    if not is_valid:
        click.echo(f"❌ Invalid project name: {error}", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "cspell_manager.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), "--setup-project", project_name]
    if project_type:
        cmd.extend(["--type", project_type])
    
    result = run_secure_command(cmd, f"Setting up CSpell for {project_name}")
    sys.exit(0 if result.success and result.security_validated else 1)


@spell.command("check")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Interactive fix mode")
def spell_check(path, fix):
    """Check spelling in files."""
    # Validation du chemin
    is_valid, error = validate_user_input(str(path), 'path')
    if not is_valid:
        click.echo(f"❌ Invalid path: {error}", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "cspell_manager.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    if fix:
        cmd = [sys.executable, str(script_path), "--fix", str(path)]
    else:
        cmd = [sys.executable, str(script_path), "--check", str(path)]
    
    result = run_secure_command(cmd, f"Spell checking {path}")
    sys.exit(0 if result.success and result.security_validated else 1)


@wom.group()
def system():
    """🔧 System detection and prerequisites."""
    pass


@system.command("detect")
@click.option("--export", type=click.Path(), help="Export report to file")
def system_detect(export):
    """Detect system information and available tools."""
    # Validation du chemin d'export si fourni
    if export:
        is_valid, error = validate_user_input(export, 'path')
        if not is_valid:
            click.echo(f"❌ Invalid export path: {error}", err=True)
            sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "system_detector.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path)]
    if export:
        cmd.extend(["--export", export])
    
    result = run_secure_command(cmd, "Detecting system information")
    sys.exit(0 if result.success and result.security_validated else 1)


@system.command("install")
@click.option("--check", is_flag=True, help="Only check prerequisites")
@click.option("--interactive", is_flag=True, help="Interactive installation mode")
@click.argument("tools", nargs=-1, type=click.Choice(["python", "node", "git", "all"]))
def system_install(check, interactive, tools):
    """Install system prerequisites."""
    script_path = Path(__file__).parent / "shared" / "prerequisite_installer.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path)]
    if check:
        cmd.append("--check")
    if interactive:
        cmd.append("--interactive")
    if tools:
        cmd.extend(["--install"] + list(tools))
    
    result = run_secure_command(cmd, "Managing system prerequisites")
    sys.exit(0 if result.success and result.security_validated else 1)


@wom.group()
def deploy():
    """📦 Deployment and distribution tools."""
    pass


@deploy.command("tools")
@click.option("--target", type=click.Path(), default="~/.dev-tools", 
              help="Target directory for deployment")
@click.option("--global", "create_global", is_flag=True, 
              help="Create global commands")
def deploy_tools(target, create_global):
    """Deploy development tools to global directory."""
    # Validation du chemin cible
    is_valid, error = validate_user_input(target, 'path')
    if not is_valid:
        click.echo(f"❌ Invalid target path: {error}", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "deploy-devtools.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), "--target", target]
    if create_global:
        cmd.append("--install-global")
    
    result = run_secure_command(cmd, f"Deploying tools to {target}")
    sys.exit(0 if result.success and result.security_validated else 1)


@wom.group()
def context():
    """🖱️ Windows context menu management."""
    pass


@context.command("register")
@click.option("--backup", is_flag=True, help="Create backup before registration")
def context_register(backup):
    """Register WOM tools in Windows context menu."""
    # Vérifier que nous sommes sur Windows
    if platform.system() != "Windows":
        click.echo("❌ Context menu operations are only supported on Windows", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "system" / "register_wom_tools.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), "--register"]
    if backup:
        cmd.append("--backup")
    
    result = run_secure_command(cmd, "Registering context menu tools")
    sys.exit(0 if result.success and result.security_validated else 1)


@context.command("unregister")
def context_unregister():
    """Unregister WOM tools from Windows context menu."""
    # Vérifier que nous sommes sur Windows
    if platform.system() != "Windows":
        click.echo("❌ Context menu operations are only supported on Windows", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "system" / "register_wom_tools.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), "--unregister"]
    result = run_secure_command(cmd, "Unregistering context menu tools")
    sys.exit(0 if result.success and result.security_validated else 1)


@context.command("list")
def context_list():
    """List registered context menu entries."""
    # Vérifier que nous sommes sur Windows
    if platform.system() != "Windows":
        click.echo("❌ Context menu operations are only supported on Windows", err=True)
        sys.exit(1)
    
    script_path = Path(__file__).parent / "shared" / "system" / "registrator.py"
    
    # Validation du script
    is_valid, error = security_validator.validate_script_execution(script_path)
    if not is_valid:
        click.echo(f"❌ Script validation failed: {error}", err=True)
        sys.exit(1)
    
    cmd = [sys.executable, str(script_path), "--list"]
    result = run_secure_command(cmd, "Listing context menu entries")
    sys.exit(0 if result.success and result.security_validated else 1)


if __name__ == "__main__":
    wom()