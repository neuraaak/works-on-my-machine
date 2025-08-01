#!/usr/bin/env python3
"""
Standardized CLI Manager for Works On My Machine.
Centralizes and standardizes system command execution.

This module replaces scattered subprocess.run() calls throughout the project
with a centralized system that provides:

- Automatic and consistent command logging
- Standardized error handling
- Cross-platform support (Windows/Linux/macOS)
- Multiple execution modes (silent, interactive, verbose)
- Timeout and resource management
- Simple and consistent API

Usage:
    from shared.cli_manager import run_command, run_silent, check_tool_available

    # Execution with full logging
    result = run_command(["git", "status"], "Git status check")

    # Silent execution for checks
    result = run_silent(["python", "--version"])

    # Tool availability check
    if check_tool_available("npm"):
        print("npm available")

Migration from subprocess:
    # Old code
    result = subprocess.run(cmd, capture_output=True, text=True)

    # New code
    result = run_command(cmd, "Action description")
"""

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class CommandResult:
    """Result of an executed command."""

    def __init__(
        self,
        returncode: int,
        stdout: str = "",
        stderr: str = "",
        command: List[str] = None,
        cwd: Optional[Path] = None,
    ):
        """Initialize a command result."""
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command or []
        self.cwd = cwd
        self.success = returncode == 0

    def __bool__(self):
        """Return a boolean representation of the result."""
        return self.success

    def __str__(self):
        """Return a string representation of the result."""
        return f"CommandResult(success={self.success}, returncode={self.returncode})"


class CLIManager:
    """Centralized manager for CLI command execution."""

    def __init__(
        self,
        default_cwd: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        capture_output: bool = True,
        check: bool = False,
        timeout: Optional[int] = None,
    ):
        """
        Initialize CLI manager.

        Args:
            default_cwd: Default working directory
            verbose: Display executed commands
            capture_output: Capture stdout/stderr
            check: Raise exception on error
            timeout: Command timeout in seconds
        """
        self.default_cwd = Path(default_cwd) if default_cwd else Path.cwd()
        self.verbose = verbose
        self.capture_output = capture_output
        self.check = check
        self.timeout = timeout
        self.system = platform.system()

    def run(
        self,
        command: Union[str, List[str]],
        description: Optional[str] = None,
        cwd: Optional[Union[str, Path]] = None,
        capture_output: Optional[bool] = None,
        check: Optional[bool] = None,
        timeout: Optional[int] = None,
        input_data: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        shell: bool = False,
        **kwargs,
    ) -> CommandResult:
        """
        Execute a command with error handling and logging.

        Args:
            command: Command to execute (string or list)
            description: Description for logging
            cwd: Working directory
            capture_output: Capture output
            check: Raise exception on error
            timeout: Timeout for this command
            input_data: Data to send to stdin
            env: Environment variables
            shell: Use shell
            **kwargs: Additional arguments for subprocess

        Returns:
            CommandResult: Execution result
        """
        # Normalize command
        if isinstance(command, str):
            if shell:
                cmd = command
            else:
                cmd = command.split()
        else:
            cmd = list(command)

        # Parameters
        run_cwd = Path(cwd) if cwd else self.default_cwd
        do_capture = (
            capture_output if capture_output is not None else self.capture_output
        )
        do_check = check if check is not None else self.check
        run_timeout = timeout if timeout is not None else self.timeout

        # Logging
        if self.verbose:
            display_desc = description or "Command execution"
            print(f"\n🔍 {display_desc}...")
            cmd_str = command if isinstance(command, str) else " ".join(cmd)
            print(f"Command: {cmd_str}")
            if run_cwd != Path.cwd():
                print(f"Directory: {run_cwd}")

        try:
            # Prepare subprocess arguments
            subprocess_args = {
                "cwd": run_cwd,
                "timeout": run_timeout,
                "text": True,
                "encoding": "utf-8",
                "errors": "replace",
                "shell": shell,
            }

            # Add valid kwargs for subprocess
            valid_subprocess_args = {
                "input",
                "env",
                "capture_output",
                "check",
                "stdin",
                "stdout",
                "stderr",
                "preexec_fn",
                "close_fds",
                "pass_fds",
                "restore_signals",
                "start_new_session",
                "group",
                "extra_groups",
                "user",
                "umask",
                "startupinfo",
                "creationflags",
            }

            for key, value in kwargs.items():
                if key in valid_subprocess_args:
                    subprocess_args[key] = value

            if do_capture:
                subprocess_args["capture_output"] = True

            if input_data:
                subprocess_args["input"] = input_data

            if env:
                subprocess_args["env"] = env

            # Execute command
            result = subprocess.run(cmd, **subprocess_args)

            # Create result
            cmd_result = CommandResult(
                returncode=result.returncode,
                stdout=getattr(result, "stdout", "") or "",
                stderr=getattr(result, "stderr", "") or "",
                command=cmd if isinstance(cmd, list) else cmd.split(),
                cwd=run_cwd,
            )

            # Result logging
            if self.verbose:
                if cmd_result.success:
                    print(f"✅ {display_desc} - SUCCESS")
                    if cmd_result.stdout.strip():
                        print(cmd_result.stdout.strip())
                else:
                    print(f"❌ {display_desc} - FAILED (code: {cmd_result.returncode})")
                    if cmd_result.stderr.strip():
                        print(f"Error: {cmd_result.stderr.strip()}")
                    if cmd_result.stdout.strip():
                        print(f"Output: {cmd_result.stdout.strip()}")

            # Check if we should raise an exception
            if do_check and not cmd_result.success:
                raise subprocess.CalledProcessError(
                    cmd_result.returncode,
                    cmd_result.command,
                    cmd_result.stdout,
                    cmd_result.stderr,
                )

            return cmd_result

        except subprocess.TimeoutExpired as e:
            if self.verbose:
                print(
                    f"⏱️ Timeout after {run_timeout}s for: {description or 'command'}"
                )
            cmd_result = CommandResult(
                returncode=-1,
                stderr=f"Timeout after {run_timeout}s",
                command=cmd if isinstance(cmd, list) else cmd.split(),
                cwd=run_cwd,
            )
            if do_check:
                raise
            return cmd_result

        except Exception as e:
            if self.verbose:
                desc_text = description or "execution"
                print(f"❌ Error during {desc_text}: {e}")
            cmd_result = CommandResult(
                returncode=-1,
                stderr=str(e),
                command=cmd if isinstance(cmd, list) else cmd.split(),
                cwd=run_cwd,
            )
            if do_check:
                raise
            return cmd_result

    def run_silent(self, command: Union[str, List[str]], **kwargs) -> CommandResult:
        """Execute a command in silent mode."""
        return self.run(command, verbose=False, capture_output=True, **kwargs)

    def run_interactive(
        self, command: Union[str, List[str]], **kwargs
    ) -> CommandResult:
        """Execute a command in interactive mode (no capture)."""
        return self.run(command, capture_output=False, **kwargs)

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available."""
        return shutil.which(command) is not None

    def get_command_version(
        self, command: str, version_flag: str = "--version"
    ) -> Optional[str]:
        """Get version of a command."""
        if not self.check_command_available(command):
            return None

        result = self.run_silent([command, version_flag])
        if result.success:
            # Extract version from output
            output = result.stdout.strip()
            if output:
                # Take first line which probably contains version
                first_line = output.split("\n")[0]
                return first_line

        return None

    def find_executable(self, names: List[str]) -> Optional[str]:
        """Find first available executable in a list."""
        for name in names:
            if self.check_command_available(name):
                return name
        return None

    def create_shell_command(
        self, script_content: str, extension: Optional[str] = None
    ) -> Path:
        """Create temporary shell script and return its path."""
        import tempfile

        if extension is None:
            extension = ".bat" if self.system == "Windows" else ".sh"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=extension, delete=False, encoding="utf-8"
        ) as f:
            f.write(script_content)
            script_path = Path(f.name)

        # Make executable on Unix
        if self.system != "Windows":
            script_path.chmod(0o755)

        return script_path


# Global instance for simple usage
default_cli = CLIManager()


def run_command(
    command: Union[str, List[str]], description: Optional[str] = None, **kwargs
) -> CommandResult:
    """Return a CommandResult for the executed command with default instance."""
    return default_cli.run(command, description, **kwargs)


def run_silent(command: Union[str, List[str]], **kwargs) -> CommandResult:
    """Return a CommandResult for the executed command silently."""
    return default_cli.run_silent(command, **kwargs)


def run_interactive(command: Union[str, List[str]], **kwargs) -> CommandResult:
    """Return a CommandResult for the executed command interactively."""
    return default_cli.run_interactive(command, **kwargs)


def check_tool_available(tool: str) -> bool:
    """Check if a tool is available."""
    return default_cli.check_command_available(tool)


def get_tool_version(tool: str, version_flag: str = "--version") -> Optional[str]:
    """Get version of a tool."""
    return default_cli.get_command_version(tool, version_flag)


# Compatibility functions to ease migration
def run_command_legacy(command, description, cwd=None):
    """Compatibility function with old run_command format."""
    result = default_cli.run(
        command=command, description=description, cwd=cwd, capture_output=True
    )
    # Return True/False like old function
    return result.success
