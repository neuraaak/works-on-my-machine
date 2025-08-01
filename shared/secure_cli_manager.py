#!/usr/bin/env python3
"""
Secure CLI Manager for Works On My Machine.
Enhanced version of cli_manager.py with comprehensive security validation.
"""

import json
import logging
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from shared.security_validator import SecurityValidator, validate_user_input, safe_command_execution


class SecureCommandResult:
    """Enhanced result of an executed command with security information."""

    def __init__(
        self,
        returncode: int,
        stdout: str = "",
        stderr: str = "",
        command: List[str] = None,
        cwd: Optional[Path] = None,
        security_validated: bool = False,
        execution_time: float = 0.0,
    ):
        """Initialize a secure command result."""
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command or []
        self.cwd = cwd
        self.success = returncode == 0
        self.security_validated = security_validated
        self.execution_time = execution_time

    def __bool__(self):
        """Return a boolean representation of the result."""
        return self.success and self.security_validated

    def __str__(self):
        """Return a string representation of the result."""
        return f"SecureCommandResult(success={self.success}, validated={self.security_validated}, time={self.execution_time:.2f}s)"


class SecureCLIManager:
    """Secure centralized manager for CLI command execution."""

    def __init__(
        self,
        default_cwd: Optional[Union[str, Path]] = None,
        verbose: bool = True,
        capture_output: bool = True,
        check: bool = False,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize secure CLI manager.

        Args:
            default_cwd: Default working directory
            verbose: Display executed commands
            capture_output: Capture stdout/stderr
            check: Raise exception on error
            timeout: Command timeout in seconds
            max_retries: Maximum number of retries for failed commands
            retry_delay: Delay between retries in seconds
        """
        self.default_cwd = Path(default_cwd) if default_cwd else Path.cwd()
        self.verbose = verbose
        self.capture_output = capture_output
        self.check = check
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.system = platform.system()
        self.security_validator = SecurityValidator()
        
        # Configuration du logging
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for security events."""
        logger = logging.getLogger('secure_cli_manager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

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
        validate_security: bool = True,
        **kwargs,
    ) -> SecureCommandResult:
        """
        Execute a command with enhanced security validation and error handling.

        Args:
            command: Command to execute (string or list)
            description: Description for logging
            cwd: Working directory
            capture_output: Capture output
            check: Raise exception on error
            timeout: Timeout for this command
            input_data: Data to send to stdin
            env: Environment variables
            shell: Use shell (not recommended for security)
            validate_security: Whether to validate command security
            **kwargs: Additional arguments for subprocess

        Returns:
            SecureCommandResult: Execution result with security information
        """
        start_time = time.time()
        
        # Normalize command
        if isinstance(command, str):
            if shell:
                cmd = command
            else:
                cmd = command.split()
        else:
            cmd = list(command)

        # Security validation
        security_validated = False
        if validate_security:
            is_valid, error = self.security_validator.validate_command(cmd)
            if not is_valid:
                self.logger.warning(f"Command validation failed: {error}")
                if self.verbose:
                    print(f"❌ Security validation failed: {error}")
                return SecureCommandResult(
                    returncode=-1,
                    stderr=f"Security validation failed: {error}",
                    command=cmd,
                    cwd=cwd,
                    security_validated=False,
                    execution_time=time.time() - start_time,
                )
            security_validated = True

        # Parameters
        run_cwd = Path(cwd) if cwd else self.default_cwd
        do_capture = (
            capture_output if capture_output is not None else self.capture_output
        )
        do_check = check if check is not None else self.check
        run_timeout = timeout if timeout is not None else self.timeout

        # Validate working directory
        if not self.security_validator.validate_path(run_cwd, must_exist=True)[0]:
            error_msg = f"Invalid working directory: {run_cwd}"
            self.logger.error(error_msg)
            return SecureCommandResult(
                returncode=-1,
                stderr=error_msg,
                command=cmd,
                cwd=run_cwd,
                security_validated=security_validated,
                execution_time=time.time() - start_time,
            )

        # Logging
        if self.verbose:
            display_desc = description or "Command execution"
            print(f"\n🔍 {display_desc}...")
            cmd_str = command if isinstance(command, str) else " ".join(cmd)
            print(f"Command: {cmd_str}")
            if run_cwd != Path.cwd():
                print(f"Directory: {run_cwd}")
            if security_validated:
                print("🔒 Security: Validated")

        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = self._execute_command(
                    cmd, run_cwd, do_capture, run_timeout, input_data, env, shell, **kwargs
                )
                
                # Log security event
                self.logger.info(
                    f"Command executed: {' '.join(cmd)} | "
                    f"Success: {result.success} | "
                    f"Validated: {security_validated} | "
                    f"Attempt: {attempt + 1}"
                )
                
                # Create secure result
                secure_result = SecureCommandResult(
                    returncode=result.returncode,
                    stdout=getattr(result, "stdout", "") or "",
                    stderr=getattr(result, "stderr", "") or "",
                    command=cmd if isinstance(cmd, list) else cmd.split(),
                    cwd=run_cwd,
                    security_validated=security_validated,
                    execution_time=time.time() - start_time,
                )

                # Result logging
                if self.verbose:
                    if secure_result.success:
                        print(f"✅ {display_desc} - SUCCESS ({secure_result.execution_time:.2f}s)")
                        if secure_result.stdout.strip():
                            print(secure_result.stdout.strip())
                    else:
                        print(f"❌ {display_desc} - FAILED (code: {secure_result.returncode})")
                        if secure_result.stderr.strip():
                            print(f"Error: {secure_result.stderr.strip()}")
                        if secure_result.stdout.strip():
                            print(f"Output: {secure_result.stdout.strip()}")

                # Check if we should raise an exception
                if do_check and not secure_result.success:
                    raise subprocess.CalledProcessError(
                        secure_result.returncode,
                        secure_result.command,
                        secure_result.stdout,
                        secure_result.stderr,
                    )

                return secure_result

            except subprocess.TimeoutExpired as e:
                last_error = e
                if self.verbose:
                    print(f"⏱️ Timeout after {run_timeout}s (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                last_error = e
                if self.verbose:
                    desc_text = description or "execution"
                    print(f"❌ Error during {desc_text} (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        # All retries failed
        error_msg = f"All {self.max_retries} attempts failed. Last error: {last_error}"
        self.logger.error(error_msg)
        
        return SecureCommandResult(
            returncode=-1,
            stderr=error_msg,
            command=cmd if isinstance(cmd, list) else cmd.split(),
            cwd=run_cwd,
            security_validated=security_validated,
            execution_time=time.time() - start_time,
        )

    def _execute_command(
        self,
        cmd: Union[str, List[str]],
        cwd: Path,
        capture_output: bool,
        timeout: Optional[int],
        input_data: Optional[str],
        env: Optional[Dict[str, str]],
        shell: bool,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        """Execute a single command attempt."""
        # Prepare subprocess arguments
        subprocess_args = {
            "cwd": cwd,
            "timeout": timeout,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "shell": shell,
        }

        # Add valid kwargs for subprocess
        valid_subprocess_args = {
            "input", "env", "capture_output", "check", "stdin", "stdout", "stderr",
            "preexec_fn", "close_fds", "pass_fds", "restore_signals",
            "start_new_session", "group", "extra_groups", "user", "umask",
            "startupinfo", "creationflags",
        }

        for key, value in kwargs.items():
            if key in valid_subprocess_args:
                subprocess_args[key] = value

        if capture_output:
            subprocess_args["capture_output"] = True

        if input_data:
            subprocess_args["input"] = input_data

        if env:
            subprocess_args["env"] = env

        # Execute command
        return subprocess.run(cmd, **subprocess_args)

    def run_silent(self, command: Union[str, List[str]], **kwargs) -> SecureCommandResult:
        """Execute a command in silent mode."""
        return self.run(command, verbose=False, capture_output=True, **kwargs)

    def run_interactive(
        self, command: Union[str, List[str]], **kwargs
    ) -> SecureCommandResult:
        """Execute a command in interactive mode (no capture)."""
        return self.run(command, capture_output=False, **kwargs)

    def run_with_validation(
        self, command: Union[str, List[str]], description: str = "", **kwargs
    ) -> SecureCommandResult:
        """Execute a command with strict security validation."""
        return self.run(
            command, description, validate_security=True, **kwargs
        )

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available and secure."""
        if not shutil.which(command):
            return False
        
        # Additional security check: validate command name
        is_valid, _ = self.security_validator.validate_command([command])
        return is_valid

    def get_command_version(
        self, command: str, version_flag: str = "--version"
    ) -> Optional[str]:
        """Get version of a command with security validation."""
        if not self.check_command_available(command):
            return None

        result = self.run_silent([command, version_flag])
        if result.success and result.security_validated:
            # Extract version from output
            output = result.stdout.strip()
            if output:
                # Take first line which probably contains version
                first_line = output.split("\n")[0]
                return first_line

        return None

    def find_executable(self, names: List[str]) -> Optional[str]:
        """Find first available and secure executable in a list."""
        for name in names:
            if self.check_command_available(name):
                return name
        return None

    def create_shell_command(
        self, script_content: str, extension: Optional[str] = None
    ) -> Path:
        """Create temporary shell script with security validation."""
        import tempfile

        # Validate script content
        if len(script_content) > 10000:  # Limit script size
            raise ValueError("Script content too large")

        # Check for dangerous patterns in script
        for pattern in self.security_validator.DANGEROUS_PATTERNS:
            if re.search(pattern, script_content):
                raise ValueError(f"Script contains dangerous pattern: {pattern}")

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
default_secure_cli = SecureCLIManager()


def run_secure_command(
    command: Union[str, List[str]], description: Optional[str] = None, **kwargs
) -> SecureCommandResult:
    """Execute a command with security validation using default instance."""
    return default_secure_cli.run(command, description, **kwargs)


def run_secure_silent(command: Union[str, List[str]], **kwargs) -> SecureCommandResult:
    """Execute a command silently with security validation."""
    return default_secure_cli.run_silent(command, **kwargs)


def run_secure_interactive(command: Union[str, List[str]], **kwargs) -> SecureCommandResult:
    """Execute a command interactively with security validation."""
    return default_secure_cli.run_interactive(command, **kwargs)


def check_tool_secure(tool: str) -> bool:
    """Check if a tool is available and secure."""
    return default_secure_cli.check_command_available(tool)


def get_tool_version_secure(tool: str, version_flag: str = "--version") -> Optional[str]:
    """Get version of a tool with security validation."""
    return default_secure_cli.get_command_version(tool, version_flag)