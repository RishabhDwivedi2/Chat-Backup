# [AI]: This file implements a project tree generator.
# It provides functionality to create a hierarchical representation of a project's file structure.
# Key features:
# - Finds the project root directory
# - Generates a tree-like structure of the project
# - Handles permissions and errors gracefully
# - Uses colorama for colored console output
# - Writes the generated tree to a markdown file

import os
from pathlib import Path
import logging
import sys
from colorama import Fore, Style, init

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Define color constants for consistent message formatting
INFO_COLOR = Fore.WHITE
SUCCESS_COLOR = Fore.GREEN
WARNING_COLOR = Fore.YELLOW
ERROR_COLOR = Fore.RED
PROMPT_COLOR = Fore.YELLOW

# [AI]: Helper functions for formatting colored messages
def format_message(message: str, color: str) -> str:
    """Format a message with the given color."""
    return f"{color}{message}{Style.RESET_ALL}"

def info_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

def success_message(message: str) -> str:
    return format_message(message, SUCCESS_COLOR)

def warning_message(header: str, message: str) -> str:
    return f"{WARNING_COLOR}{header}{Style.RESET_ALL} {message}"

def error_message(message: str) -> str:
    return format_message(message, ERROR_COLOR)

def file_path_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

# [AI]: Set up logging for tracking script execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Increase recursion limit to handle deep directory structures
sys.setrecursionlimit(10000)

# [AI]: Function to find the project root directory
def find_project_root(start_path: Path) -> Path:
    """
    Traverse up the directory tree to find the project root.
    The root is identified by the presence of a .git directory or pyproject.toml file.
    """
    current_path = start_path.resolve()
    while current_path != current_path.parent:
        if (current_path / '.git').exists() or (current_path / 'pyproject.toml').exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Could not find project root. Make sure you're in a git repository or have a pyproject.toml file.")

# [AI]: Function to generate the project tree structure
def get_project_tree(path: Path, indent_level: int = 0, top_level_only: set = None) -> list:
    """
    Recursively generate a tree-like structure of the project directory.
    Handles permissions and errors, and skips certain directories.
    """
    if top_level_only is None:
        top_level_only = {"node_modules", ".next", "venv", ".ai", "alembic"}
    
    tree = []
    try:
        # [AI]: Sort items alphabetically, with directories first
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        logger.warning(warning_message("Warning:", f"Permission denied: {path}"))
        return tree
    except Exception as e:
        logger.error(error_message(f"Error accessing {path}: {e}"))
        return tree
    
    for item in items:
        if item.name == "__pycache__":
            continue
        
        indent = "    " * indent_level
        if item.is_dir():
            tree.append(f"{indent}├── {item.name}/")
            if item.name not in top_level_only:
                tree.extend(get_project_tree(item, indent_level + 1, top_level_only))
        else:
            tree.append(f"{indent}├── {item.name}")
    
    return tree

# [AI]: Main function to orchestrate the project tree generation and file writing
def main():
    print(info_message("\nStarting update_project_tree.py\n"))
    
    # [AI]: Find the project root directory
    script_path = Path(__file__).resolve()
    try:
        root_dir = find_project_root(script_path)
    except FileNotFoundError as e:
        print(error_message(str(e)))
        return

    # [AI]: Get the project name from the root directory
    project_name = root_dir.name

    # [AI]: Generate the project tree
    print(info_message("Generating project tree..."))
    tree_output = [project_name.upper()]
    tree_output.extend(get_project_tree(root_dir))
    print(f"{SUCCESS_COLOR}Generated:{Style.RESET_ALL} Project tree generated successfully")

    # [AI]: Define the output file path
    output_path = root_dir / "workspace" / "files" / "project_tree.md"

    # [AI]: Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # [AI]: Write the generated tree to a markdown file
    try:
        with output_path.open("w", encoding="utf-8") as f:
            f.write("```markdown\n")
            f.write("\n".join(tree_output))
            f.write("\n```")
        relative_path = output_path.relative_to(root_dir)
        print(f"{SUCCESS_COLOR}Updated:{Style.RESET_ALL} Project tree in {file_path_message(str(relative_path))}")
    except IOError as e:
        print(error_message(f"Error writing to file: {e}"))

    print(success_message("\nProject tree update completed successfully."))
    print()  # Add a final line break

# [AI]: Entry point of the script
if __name__ == "__main__":
    main()
