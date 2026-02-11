#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERACTIVE WIZARD - Context Menu Interactive Wizard
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Interactive wizard for context menu configuration.

This module provides an interactive step-by-step wizard for configuring
context menu entries, making it easy for users to set up their scripts
without needing to know all the technical details.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

try:
    from InquirerPy import inquirer
    from InquirerPy.validator import PathValidator

    INQUIRERPY_AVAILABLE = True
except ImportError:
    INQUIRERPY_AVAILABLE = False

# Local imports
from ...services.context import ContextParametersService, ContextType
from ..common.ezpl_bridge import ezconsole, ezprinter
from ..common.interactive_menu import InteractiveMenu

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ContextMenuWizard:
    """Interactive wizard for context menu configuration."""

    @staticmethod
    def run_setup() -> (
        tuple[str | None, str | None, str | None, ContextParametersService | None]
    ):
        """
        Run the complete interactive setup wizard.

        Returns:
            Tuple of (script_path, label, icon, context_params) or (None, None, None, None) if cancelled
        """
        ezprinter.info("🎯 Interactive Context Menu Setup")
        ezprinter.info("=" * 50)

        # Step 1: Select script file
        ezconsole.print("", style="dim")
        ezconsole.print("📁 Step 1: Select script file", style="bold blue")
        script_path = ContextMenuWizard._select_script()
        if not script_path:
            return None, None, None, None

        # Step 2: Enter label
        ezconsole.print("\n" + (":" * 80) + "\n", style="dim")
        ezconsole.print("🏷️  Step 2: Enter display label", style="bold blue")
        label = ContextMenuWizard._get_label()
        if not label:
            return None, None, None, None

        # Step 3: Select icon
        ezconsole.print("\n" + (":" * 80) + "\n", style="dim")
        ezconsole.print("🎨 Step 3: Select icon", style="bold blue")
        icon = ContextMenuWizard._select_icon(script_path)

        # Step 4: Select context type
        ezconsole.print("\n" + (":" * 80) + "\n", style="dim")
        ezconsole.print("🎯 Step 4: Select context type", style="bold blue")
        context_params = ContextMenuWizard._select_context()

        return script_path, label, icon, context_params

    @staticmethod
    def _select_script() -> str | None:
        """Interactive script file selection."""
        if INQUIRERPY_AVAILABLE:
            # Use InquirerPy for better file selection
            return ContextMenuWizard._select_script_with_inquirer()
        else:
            # Fallback to custom menu
            return ContextMenuWizard._select_script_fallback()

    @staticmethod
    def _select_script_with_inquirer() -> str | None:
        """Select script using InquirerPy file browser."""
        try:
            # Create a custom validator for script files
            class ScriptFileValidator(PathValidator):
                def __init__(self):
                    super().__init__()
                    self.script_extensions = {".py", ".bat", ".ps1", ".exe", ".cmd"}

                def validate(self, document):
                    result = super().validate(document)
                    if result:
                        path = Path(document.text)
                        if (
                            path.is_file()
                            and path.suffix.lower() in self.script_extensions
                        ):
                            return True
                        else:
                            raise ValueError(
                                f"File must be a script ({', '.join(self.script_extensions)})"
                            )
                    return result

            # Use InquirerPy file browser
            script_path = (
                inquirer.filepath(  # pyright: ignore[reportPrivateImportUsage]
                    message="Select script file:",
                    default=str(Path.cwd()),
                    validate=ScriptFileValidator(),
                    only_files=True,
                    only_directories=False,
                    transformer=lambda result: str(Path(result).resolve()),
                    filter=lambda result: str(Path(result).resolve()),
                ).execute()
            )

            if script_path:
                return script_path
            else:
                ezprinter.info("File selection cancelled")
                return None

        except Exception as e:
            ezprinter.error(f"Error with file browser: {e}")
            ezprinter.info("Falling back to manual input...")
            return ContextMenuWizard._select_script_fallback()

    @staticmethod
    def _select_script_fallback() -> str | None:
        """Fallback script selection using custom menu."""
        menu = InteractiveMenu(
            title="Select Script File",
            instruction="Choose how to specify the script file",
        )

        items = [
            {"label": "Browse current directory", "value": "browse"},
            {"label": "Enter path manually", "value": "manual"},
            {"label": "Cancel", "value": "cancel"},
        ]

        selected = menu.select_from_list(items, display_func=lambda item: item["label"])
        if not selected:
            return None

        if selected["value"] == "browse":
            return ContextMenuWizard._browse_for_script()
        elif selected["value"] == "manual":
            ezprinter.info("Enter the full path to your script:")
            path = input("> ").strip()
            if path and Path(path).exists():
                return path
            else:
                ezprinter.error("Invalid path or file not found")
                return None
        else:  # Cancel
            return None

    @staticmethod
    def _browse_for_script() -> str | None:
        """Browse for script files in current directory."""
        current_dir = Path.cwd()

        # Supported script extensions
        script_extensions = {".py", ".bat", ".ps1", ".exe", ".cmd"}

        # Find script files in current directory
        script_files = [
            file
            for file in current_dir.iterdir()
            if file.is_file() and file.suffix.lower() in script_extensions
        ]

        if not script_files:
            ezprinter.error("No script files found in current directory")
            ezprinter.info(f"Current directory: {current_dir}")
            ezprinter.info(f"Supported extensions: {', '.join(script_extensions)}")
            return None

        # Sort files by name
        script_files.sort(key=lambda x: x.name.lower())

        # Create selection menu
        menu = InteractiveMenu(
            title="Select Script File",
            instruction=f"Found {len(script_files)} script files in {current_dir.name}",
        )

        items = []
        for file in script_files:
            file_info = f"{file.name} ({file.suffix.upper()})"
            items.append({"label": file_info, "type": "file", "path": file})

        items.append(
            {
                "label": "📁 Browse parent directory",
                "type": "parent",
                "path": current_dir.parent,
            }
        )
        items.append({"label": "❌ Cancel", "type": "cancel", "path": None})

        selected = menu.select_from_list(items, display_func=lambda item: item["label"])
        if not selected or selected["type"] == "cancel":
            return None

        if selected["type"] == "file":
            return str(selected["path"].resolve())
        if selected["type"] == "parent":
            parent_dir = selected["path"]
            if parent_dir != current_dir:  # Not at root
                return ContextMenuWizard._browse_directory(parent_dir)
            ezprinter.error("Already at root directory")
            return None
        return None

    @staticmethod
    def _browse_directory(directory: Path) -> str | None:
        """Browse a specific directory for script files."""
        if not directory.exists() or not directory.is_dir():
            ezprinter.error(f"Invalid directory: {directory}")
            return None

        # Supported script extensions
        script_extensions = {".py", ".bat", ".ps1", ".exe", ".cmd"}

        # Get subdirectories and script files
        subdirs = []
        script_files = []

        try:
            for item in directory.iterdir():
                if item.is_dir():
                    subdirs.append(item)
                elif item.is_file() and item.suffix.lower() in script_extensions:
                    script_files.append(item)
        except PermissionError:
            ezprinter.error(f"Permission denied accessing directory: {directory}")
            return None

        # Sort items
        subdirs.sort(key=lambda x: x.name.lower())
        script_files.sort(key=lambda x: x.name.lower())

        # Create options list
        items = []

        # Add parent directory option (if not at root)
        if directory.parent != directory:
            items.append(
                {
                    "label": "📁 .. (Parent directory)",
                    "type": "parent",
                    "path": directory.parent,
                }
            )

        # Add subdirectories
        for subdir in subdirs:
            items.append({"label": f"📁 {subdir.name}/", "type": "dir", "path": subdir})

        # Add script files
        for file in script_files:
            items.append(
                {
                    "label": f"📄 {file.name} ({file.suffix.upper()})",
                    "type": "file",
                    "path": file,
                }
            )

        # Add cancel option
        items.append({"label": "❌ Cancel", "type": "cancel", "path": None})

        if not script_files and not subdirs:
            ezprinter.error(f"No script files or subdirectories found in {directory}")
            return None

        # Show selection menu
        menu = InteractiveMenu(
            title="Browse Directory",
            instruction=f"Current: {directory} | Files: {len(script_files)} | Dirs: {len(subdirs)}",
        )

        selected = menu.select_from_list(items, display_func=lambda item: item["label"])
        if not selected or selected["type"] == "cancel":
            return None

        if selected["type"] == "file":
            return str(selected["path"].resolve())
        if selected["type"] in {"dir", "parent"}:
            return ContextMenuWizard._browse_directory(selected["path"])
        return None

    @staticmethod
    def _get_label() -> str | None:
        """Interactive label input."""
        if INQUIRERPY_AVAILABLE:
            return ContextMenuWizard._get_label_with_inquirer()
        else:
            return ContextMenuWizard._get_label_fallback()

    @staticmethod
    def _get_label_with_inquirer() -> str | None:
        """Get label using InquirerPy."""
        try:
            label = inquirer.text(  # pyright: ignore[reportPrivateImportUsage]
                message="Enter the label to display in the context menu:",
                validate=lambda result: len(result.strip()) > 0 if result else False,
                invalid_message="Label cannot be empty",
                filter=lambda result: result.strip(),
            ).execute()

            return label if label else None

        except Exception as e:
            ezprinter.error(f"Error with label input: {e}")
            ezprinter.info("Falling back to manual input...")
            return ContextMenuWizard._get_label_fallback()

    @staticmethod
    def _get_label_fallback() -> str | None:
        """Fallback label input."""
        ezprinter.info("Enter the label to display in the context menu:")
        label = input("> ").strip()
        if not label:
            ezprinter.error("Label cannot be empty")
            return None
        return label

    @staticmethod
    def _select_icon(_script_path: str) -> str | None:
        """Interactive icon selection."""
        # Note: script_path is kept for future use when auto-detecting script icons
        if INQUIRERPY_AVAILABLE:
            return ContextMenuWizard._select_icon_with_inquirer()
        else:
            return ContextMenuWizard._select_icon_fallback()

    @staticmethod
    def _select_icon_with_inquirer() -> str | None:
        """Select icon using InquirerPy."""
        try:
            # First, ask for icon type
            icon_type = inquirer.select(  # pyright: ignore[reportPrivateImportUsage]
                message="Choose icon type:",
                choices=[
                    {"name": "Auto-detect (recommended)", "value": "auto"},
                    {"name": "Use script's own icon", "value": "script"},
                    {"name": "Browse for icon file", "value": "browse"},
                    {"name": "Enter custom path", "value": "manual"},
                    {"name": "No icon", "value": "none"},
                ],
                default="auto",
            ).execute()

            if icon_type == "auto":
                return "auto"
            elif icon_type == "script":
                return "script"
            elif icon_type == "none":
                return None
            elif icon_type == "browse":
                # Use InquirerPy file browser for icon files
                class IconFileValidator(PathValidator):
                    def __init__(self):
                        super().__init__()
                        self.icon_extensions = {
                            ".ico",
                            ".exe",
                            ".dll",
                            ".png",
                            ".jpg",
                            ".jpeg",
                        }

                    def validate(self, document):
                        result = super().validate(document)
                        if result:
                            path = Path(document.text)
                            if (
                                path.is_file()
                                and path.suffix.lower() in self.icon_extensions
                            ):
                                return True
                            else:
                                raise ValueError(
                                    f"File must be an icon ({', '.join(self.icon_extensions)})"
                                )
                        return result

                icon_path = (
                    inquirer.filepath(  # pyright: ignore[reportPrivateImportUsage]
                        message="Select icon file:",
                        default=str(Path.cwd()),
                        validate=IconFileValidator(),
                        only_files=True,
                        only_directories=False,
                        transformer=lambda result: str(Path(result).resolve()),
                        filter=lambda result: str(Path(result).resolve()),
                    ).execute()
                )

                return icon_path if icon_path else "auto"
            else:  # manual
                icon_path = inquirer.text(  # pyright: ignore[reportPrivateImportUsage]
                    message="Enter icon file path:",
                    validate=lambda result: Path(result).exists() if result else True,
                ).execute()

                return icon_path if icon_path else "auto"

        except Exception as e:
            ezprinter.error(f"Error with icon selection: {e}")
            ezprinter.info("Falling back to manual input...")
            return ContextMenuWizard._select_icon_fallback()

    @staticmethod
    def _select_icon_fallback() -> str | None:
        """Fallback icon selection using custom menu."""
        menu = InteractiveMenu(
            title="Select Icon", instruction="Choose icon for the context menu entry"
        )

        items = [
            {"label": "Auto-detect (recommended)", "value": "auto"},
            {"label": "Use script's own icon", "value": "script"},
            {"label": "Enter custom icon path", "value": "manual"},
            {"label": "No icon", "value": "none"},
        ]

        selected = menu.select_from_list(items, display_func=lambda item: item["label"])
        if not selected:
            return None

        if selected["value"] == "auto":
            return "auto"
        elif selected["value"] == "script":
            return "script"
        elif selected["value"] == "manual":
            ezprinter.info("Enter the path to your icon file (.ico, .exe, etc.):")
            icon_path = input("> ").strip()
            return icon_path if icon_path else "auto"
        else:
            return None

    @staticmethod
    def _select_context() -> ContextParametersService:
        """Interactive context type selection."""
        menu = InteractiveMenu(
            title="Select Context Type",
            instruction="Choose where this script should appear",
        )

        context_options = [
            {"label": "Directory + Background (default)", "value": 0},
            {"label": "Files only", "value": 1},
            {"label": "Directories only", "value": 2},
            {"label": "Background only", "value": 3},
            {"label": "Root directories (drives)", "value": 4},
            {"label": "Custom file types", "value": 5},
        ]

        selected = menu.select_from_list(
            context_options, display_func=lambda item: item["label"]
        )

        context_params = ContextParametersService()

        if not selected:
            return context_params

        choice = selected["value"]

        if choice == 0:  # Default
            context_params.add_context_type(ContextType.DIRECTORY)
            context_params.add_context_type(ContextType.BACKGROUND)
        elif choice == 1:  # Files
            context_params.add_context_type(ContextType.FILE)
        elif choice == 2:  # Directories
            context_params.add_context_type(ContextType.DIRECTORY)
        elif choice == 3:  # Background
            context_params.add_context_type(ContextType.BACKGROUND)
        elif choice == 4:  # Root
            context_params.add_context_type(ContextType.ROOT)
        elif choice == 5:  # Custom file types
            context_params.add_context_type(ContextType.FILE)
            ContextMenuWizard._select_file_types(context_params)

        return context_params

    @staticmethod
    def _select_file_types(context_params: ContextParametersService) -> None:
        """Interactive file type selection."""
        menu = InteractiveMenu(
            title="Select File Types", instruction="Choose which file types to support"
        )

        file_type_options = [
            {"label": "Images (.jpg, .png, .gif, etc.)", "value": "image"},
            {"label": "Text files (.txt, .md, .py, etc.)", "value": "text"},
            {"label": "Archives (.zip, .rar, .7z, etc.)", "value": "archive"},
            {"label": "Documents (.pdf, .doc, .xls, etc.)", "value": "document"},
            {"label": "Media files (.mp3, .mp4, .avi, etc.)", "value": "media"},
            {"label": "Code files (.py, .js, .java, etc.)", "value": "code"},
            {"label": "Custom extensions", "value": "custom"},
        ]

        selected = menu.select_from_list(
            file_type_options, display_func=lambda item: item["label"]
        )

        if not selected:
            return

        choice = selected["value"]

        if choice == "image":
            context_params.add_file_type("image")
        elif choice == "text":
            context_params.add_file_type("text")
        elif choice == "archive":
            context_params.add_file_type("archive")
        elif choice == "document":
            context_params.add_file_type("document")
        elif choice == "media":
            context_params.add_file_type("media")
        elif choice == "code":
            context_params.add_file_type("code")
        elif choice == "custom":
            ezprinter.info("Enter custom extensions (e.g., .py .js .txt):")
            extensions = input("> ").strip().split()
            for ext in extensions:
                context_params.add_file_type(ext)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextMenuWizard"]
