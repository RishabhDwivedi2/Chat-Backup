# [AI]: This file implements a backup restoration system for a project.
# It provides functionality to list available backups and restore a selected backup.
# Key features:
# - Colored console output for better user experience
# - Logging of restoration process
# - Exclusion of specific files and directories from restoration
# - Interactive backup selection
# - Progress bar for restoration process

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

# [AI]: Load settings from configuration files
PROJECT_ROOT = Path(__file__).parents[2]
settings = Dynaconf(settings_files=[
    str(PROJECT_ROOT / "backend/config/settings.toml"),
    str(PROJECT_ROOT / "backend/config/settings.lcl.toml")
])

# [AI]: Extract relevant settings for backup and restoration
PROJECT_NAME = settings.PROJECT.NAME
BACKUP_DIRECTORY = Path(settings.BACKUP.DIRECTORY)
BACKUP_PREFIX = settings.BACKUP.PREFIX.format(PROJECT_NAME=PROJECT_NAME)
EXCLUDE_CONTENT = set(settings.BACKUP.EXCLUDE_CONTENT)
EXCLUDE_EXTENSIONS = set(settings.BACKUP.EXCLUDE_EXTENSIONS)

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

# [AI]: Set up logging for the restoration process
def setup_logging():
    """
    Set up logging configuration for both file and console output.
    Returns a configured logger object.
    """
    log_dir = PROJECT_ROOT / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / settings.BACKUP_LOGS.RESTORE_LOG

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

# [AI]: Get a list of available backups sorted by modification time
def get_backups(backup_dir: Path) -> List[Path]:
    """
    Retrieve a list of backup directories sorted by modification time (newest first).
    """
    return sorted(
        [item for item in backup_dir.iterdir() if item.is_dir() and item.name.startswith(BACKUP_PREFIX)],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

# [AI]: Check if a file or directory should be restored based on exclusion rules
def should_restore(path: Path) -> bool:
    """
    Determine if a file or directory should be restored based on exclusion rules.
    """
    return not any(part in EXCLUDE_CONTENT for part in path.parts) and path.suffix not in EXCLUDE_EXTENSIONS

# [AI]: Perform the actual restoration process
def restore_backup(backup_path: Path, project_root: Path, logger: logging.Logger):
    """
    Restore files and directories from the selected backup to the project root.
    Displays a progress bar and logs the restoration process.
    """
    print(info_message("\nStarting restoration from:"), file_path_message(str(backup_path)))
    print()  # Add an extra line for spacing
    
    # [AI]: Iterate through all files and directories in the backup
    for src in tqdm(list(backup_path.rglob('*')), desc="Restoring", 
                    bar_format="{l_bar}{bar:20}| {n_fmt}/{total_fmt}",
                    disable=None):
        if not should_restore(src.relative_to(backup_path)):
            continue

        relative_path = src.relative_to(backup_path)
        dest = project_root / relative_path
        
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {relative_path}")
        elif src.is_file():
            if src.stat().st_size == 0:
                logger.debug(f"Skipped empty file: {relative_path}")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                logger.debug(f"Restored: {relative_path}")

    print(success_message("\nRestoration completed from:"), file_path_message(str(backup_path)))
    print()  # Add an extra line for spacing

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

# [AI]: Main function to orchestrate the backup restoration process
def main():
    logger = setup_logging()
    print(success_message("\nStarting backup restoration process"))
    
    # [AI]: Add this check for the backup directory
    if not check_backup_directory():
        return

    backups = get_backups(BACKUP_DIRECTORY)
    
    if not backups:
        print(warning_message("\nWARNING:", "No backups found."))
        print()  # Add a line break after the warning
        return

    # [AI]: Display available backups to the user
    print(info_message("Available backups:"))
    for i, backup in enumerate(backups):
        mod_time = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(success_message(f"{i + 1}. {backup.name}"), f"(Modified: {mod_time})")

    # [AI]: Interactive loop for backup selection and confirmation
    while True:
        choice = input(prompt_message("\nEnter the number of the backup to restore or 'q' to quit: "))
        
        if choice.lower() == 'q':
            print(info_message("Exiting backup restoration process.\n"))
            break

        try:
            index = int(choice) - 1
            if 0 <= index < len(backups):
                selected_backup = backups[index]
                print(success_message("Selected backup:"), file_path_message(selected_backup.name), end='')
                confirm = input(prompt_message(" Are you sure you want to restore this backup? (y/n): "))
                if confirm.lower() == 'y':
                    restore_backup(selected_backup, PROJECT_ROOT, logger)
                    break
                else:
                    print(warning_message("WARNING:", "Restoration cancelled."))
            else:
                print(error_message("Invalid backup number. Please try again."))
        except ValueError:
            print(error_message("Invalid input. Please enter a number or 'q' to quit."))

    print(success_message("Backup restoration process completed."))
    print()  # Add a final line break

if __name__ == "__main__":
    main()