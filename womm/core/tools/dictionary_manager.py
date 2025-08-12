#!/usr/bin/env python3
"""
Dictionary Manager for CSpell - Manages custom dictionaries.
Adds all dictionary files from .cspell-dict/ to CSpell configuration.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

from .cspell_manager import add_words_from_file


def add_all_dictionaries(project_path: Optional[Path] = None) -> bool:
    """
    Add all dictionary files from .cspell-dict/ to CSpell configuration.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        bool: True if successful, False otherwise
    """
    if project_path is None:
        project_path = Path.cwd()

    cspell_dict_dir = project_path / ".cspell-dict"

    # Check if .cspell-dict directory exists
    if not cspell_dict_dir.exists():
        print("[ERROR] .cspell-dict directory not found")
        print("[TIP] Create the directory and add dictionary files (.txt)")
        print(f"[INFO] Expected location: {cspell_dict_dir}")
        return False

    if not cspell_dict_dir.is_dir():
        print(f"[ERROR] {cspell_dict_dir} is not a directory")
        return False

    print("[INFO] Searching for dictionaries in .cspell-dict/...")

    # Find all .txt files
    dict_files = list(cspell_dict_dir.glob("*.txt"))

    if not dict_files:
        print("[WARN] No dictionary files found in .cspell-dict/")
        print("[TIP] Add .txt files with one word per line")
        return False

    print(f"[INFO] Found {len(dict_files)} dictionary files:")
    for file in dict_files:
        print(f"   - {file.name}")

    # Evaluate before execution
    print(f"\n[EVAL] Will add {len(dict_files)} dictionaries to CSpell configuration")
    print("[EVAL] This will update cspell.json with new words")

    # Ask for confirmation (optional, can be skipped with --force)
    try:
        response = input("[CONFIRM] Continue? (y/N): ").strip().lower()
        if response not in ["y", "yes"]:
            print("[INFO] Operation cancelled by user")
            return False
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        return False

    # Process each dictionary file
    success_count = 0
    error_count = 0

    for dict_file in dict_files:
        print(f"\n[PROCESS] Adding dictionary: {dict_file.name}")
        try:
            success = add_words_from_file(project_path, dict_file)
            if success:
                print(f"[OK] {dict_file.name} added successfully")
                success_count += 1
            else:
                print(f"[WARN] Issue with {dict_file.name}")
                error_count += 1
        except Exception as e:
            print(f"[ERROR] Error with {dict_file.name}: {e}")
            error_count += 1

    # Summary
    print("\n[SUMMARY] Process completed:")
    print(f"   - Success: {success_count}")
    print(f"   - Errors: {error_count}")
    print(f"   - Total: {len(dict_files)}")

    if error_count == 0:
        print("[SUCCESS] All dictionaries added successfully!")
        return True
    elif success_count > 0:
        print("[PARTIAL] Some dictionaries added successfully")
        return True
    else:
        print("[FAILED] No dictionaries could be added")
        return False


def list_available_dictionaries(project_path: Optional[Path] = None) -> List[Path]:
    """
    List all available dictionary files in .cspell-dict/.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        List[Path]: List of dictionary file paths
    """
    if project_path is None:
        project_path = Path.cwd()

    cspell_dict_dir = project_path / ".cspell-dict"

    if not cspell_dict_dir.exists() or not cspell_dict_dir.is_dir():
        return []

    return list(cspell_dict_dir.glob("*.txt"))


def get_dictionary_info(project_path: Optional[Path] = None) -> dict:
    """
    Get information about available dictionaries.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        dict: Dictionary information
    """
    if project_path is None:
        project_path = Path.cwd()

    cspell_dict_dir = project_path / ".cspell-dict"

    info = {
        "directory_exists": cspell_dict_dir.exists(),
        "directory_path": str(cspell_dict_dir),
        "files": [],
        "total_files": 0,
        "total_words": 0,
    }

    if not info["directory_exists"]:
        return info

    dict_files = list_available_dictionaries(project_path)
    info["files"] = [str(f) for f in dict_files]
    info["total_files"] = len(dict_files)

    # Count words in each file
    for dict_file in dict_files:
        try:
            with open(dict_file, encoding="utf-8") as f:
                words = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
                info["total_words"] += len(words)
        except Exception as e:
            logging.debug(f"Failed to read dictionary file {dict_file}: {e}")

    return info


if __name__ == "__main__":
    # Command line interface
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        dict_files = list_available_dictionaries()
        if dict_files:
            print("Available dictionaries:")
            for file in dict_files:
                print(f"  - {file.name}")
        else:
            print("No dictionaries found")
    else:
        success = add_all_dictionaries()
        sys.exit(0 if success else 1)
