# [AI]: This file implements an automated update process for multiple project-related scripts.
# It provides functionality to run a series of update scripts sequentially.
# Key features:
# - Colored console output for better readability
# - Error handling and logging for each script execution
# - Modular design allowing easy addition of new update scripts

import subprocess
import sys
from pathlib import Path
import logging
from colorama import Fore, Style, init
from typing import List

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

# [AI]: Function to run an individual update script
def run_script(script_name: str) -> None:
    script_path = Path(__file__).parent / script_name
    print(info_message(f"Running {script_name}..."))
    try:
        # [AI]: Execute the script as a subprocess and capture its output
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(success_message(f"Successfully ran {script_name}"))
        if result.stdout:
            print(info_message(f"Output from {script_name}:"))
            print(file_path_message(result.stdout.strip()))
    except subprocess.CalledProcessError as e:
        # [AI]: Handle and display any errors that occur during script execution
        print(error_message(f"Error running {script_name}: {e}"))
        if e.stdout:
            print(info_message(f"Output from {script_name}:"))
            print(file_path_message(e.stdout.strip()))
        if e.stderr:
            print(error_message(f"Error output from {script_name}:"))
            print(file_path_message(e.stderr.strip()))

# [AI]: Main function to orchestrate the execution of all update scripts
def main() -> None:
    print(info_message("\nStarting update_all.py\n"))
    # [AI]: List of update scripts to be executed
    scripts: List[str] = [
        "update_api_specs.py",
        "update_database_schema.py",
        "update_project_tree.py",
        "update_tech_stack.py"
    ]

    # [AI]: Execute each script in the list sequentially
    for script in scripts:
        run_script(script)
    
    print(success_message("\nAll update scripts have been executed."))
    print()  # Add a final line break

if __name__ == "__main__":
    main()
