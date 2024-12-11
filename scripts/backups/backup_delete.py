# [AI]: This file implements a backup deletion system for a project.
# It provides functionality to list, select, and delete project backups.
# Key features:
# - Colored console output for better readability
# - Logging of deletion operations
# - Interactive backup selection process
# - Confirmation before deletion
# - Error handling and reporting

import os
import logging
import shutil
from pathlib import Path
from dynaconf import Dynaconf
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style, init
from typing import List

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Define color constants for different types of messages
INFO_COLOR = Fore.WHITE
SUCCESS_COLOR = Fore.GREEN
WARNING_COLOR = Fore.YELLOW
ERROR_COLOR = Fore.RED
PROMPT_COLOR = Fore.YELLOW

# [AI]: Load project settings from configuration files
PROJECT_ROOT = Path(__file__).parents[2]
settings = Dynaconf(settings_files=[
    str(PROJECT_ROOT / "backend/config/settings.toml"),
    str(PROJECT_ROOT / "backend/config/settings.lcl.toml")
])

# [AI]: Extract project-specific settings
PROJECT_NAME = settings.PROJECT.NAME
BACKUP_DIRECTORY = Path(settings.BACKUP.DIRECTORY)
BACKUP_PREFIX = settings.BACKUP.PREFIX.format(PROJECT_NAME=PROJECT_NAME)

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

def prompt_message(message: str) -> str:
    return format_message(message, PROMPT_COLOR)

def file_path_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

# [AI]: Set up logging for the backup deletion process
def setup_logging():
    """
    Configure logging for both file and console output.
    Returns a configured logger object.
    """
    log_dir = PROJECT_ROOT / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / settings.BACKUP_LOGS.DELETE_LOG

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter(settings.LOGGING.FORMAT)
    console_formatter = logging.Formatter('%(message)s')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# [AI]: Retrieve and sort available backups
def get_backups(backup_dir: Path) -> List[Path]:
    """
    Get a list of backup directories, sorted by modification time (newest first).
    """
    return sorted(
        [item for item in backup_dir.iterdir() if item.is_dir() and item.name.startswith(BACKUP_PREFIX)],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

# [AI]: Delete a single backup directory
def delete_backup(backup_path: Path, logger: logging.Logger):
    """
    Delete a backup directory and log the process.
    Handles errors during deletion and reports them.
    """
    print(info_message("\nStarting deletion of:"), file_path_message(str(backup_path)))
    
    try:
        shutil.rmtree(backup_path, onerror=lambda func, path, exc_info: logger.error(f"Error deleting {path}: {exc_info[1]}"))
        print(success_message("Deletion completed for:"), file_path_message(str(backup_path)))
    except Exception as e:
        print(error_message(f"Error during deletion of {backup_path}: {str(e)}"))

# [AI]: Add this new function to check for the backup directory
def check_backup_directory():
    print()  # Add a line break before the first message
    if not BACKUP_DIRECTORY.exists():
        print(warning_message("WARNING:", f"Backup folder at this path does not exist: {file_path_message(str(BACKUP_DIRECTORY))}"))
        print(prompt_message("You have two options:"))
        print(info_message("1. Update the path in backend/config/settings.lcl.toml if this is not the correct path."))
        print(info_message("2. Create a backup folder if you would like to have backups for this project."))
        print()
        print(prompt_message("To create a backup folder, use the following command:"))
        print(file_path_message("python scripts/backups/backup_create_folder.py"))
        print()
        print(prompt_message("After updating the path or creating the folder, run this script again."))
        print()  # Add a line break after the last message
        return False
    return True

# [AI]: Main function to orchestrate the backup deletion process
def main():
    logger = setup_logging()
    print(success_message("\nStarting backup deletion process"))
    
    # [AI]: Add this check for the backup directory
    if not check_backup_directory():
        return

    backups = get_backups(BACKUP_DIRECTORY)
    
    if not backups:
        print(warning_message("\nWARNING:", "No backups found."))
        return

    # [AI]: Display available backups with their modification times
    print(info_message("\nAvailable backups:"))
    for i, backup in enumerate(backups):
        mod_time = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(success_message(f"{i + 1}. {backup.name}"), f"(Modified: {mod_time})")

    # [AI]: Interactive loop for backup selection and deletion
    while True:
        choice = input(prompt_message("\nEnter the numbers of the backups to delete (comma-separated) or 'q' to quit: "))
        
        if choice.lower() == 'q':
            print(info_message("Exiting backup deletion process."))
            break

        try:
            # [AI]: Parse user input and select corresponding backups
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            selected_backups = [backups[i] for i in indices if 0 <= i < len(backups)]
            
            if not selected_backups:
                print(error_message("No valid backups selected. Please try again."))
                continue

            # [AI]: Display selected backups and ask for confirmation
            print(info_message("\nSelected backups for deletion:"))
            for backup in selected_backups:
                print(file_path_message(f"- {backup.name}"))
            
            confirm = input(prompt_message("\nAre you sure you want to delete these backups? (y/n): "))
            if confirm.lower() == 'y':
                # [AI]: Perform deletion of confirmed backups
                for backup in selected_backups:
                    delete_backup(backup, logger)
                    backups.remove(backup)
            else:
                print(warning_message("WARNING:", "Deletion cancelled."))
        except ValueError:
            print(error_message("Invalid input. Please enter comma-separated numbers or 'q' to quit."))

    print(success_message("Backup deletion process completed."))
    print()  # Add an extra line for spacing

if __name__ == "__main__":
    main()
