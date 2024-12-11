# [AI]: This file implements a BackupViewer class for managing and viewing project backups.
# It provides functionality to list available backups, select a backup to view,
# and open the selected backup in a separate VSCode window for inspection.
# Key features:
# - Uses Dynaconf to load configuration settings from TOML files
# - Copies selected backup to a temporary directory before viewing
# - Opens the backup in a new VSCode window
# - Implements error handling and graceful exits
# - Uses tqdm for progress bars during file operations

import os
import logging
import subprocess
import tempfile
import shutil
import sys
import time
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import signal
from colorama import Fore, Style, init
from typing import List, Optional
from dynaconf import Dynaconf
import psutil

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

def prompt_message(message: str) -> str:
    return format_message(message, PROMPT_COLOR)

def file_path_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

# [AI]: Load configuration settings from TOML files using Dynaconf
PROJECT_ROOT = Path(__file__).parents[2]
settings = Dynaconf(settings_files=[
    str(PROJECT_ROOT / "backend/config/settings.toml"),
    str(PROJECT_ROOT / "backend/config/settings.lcl.toml")
])

class BackupViewer:
    def __init__(self):
        # [AI]: Initialize BackupViewer with settings from configuration files
        self.project_name = settings.PROJECT.NAME
        self.backup_directory = Path(settings.BACKUP.DIRECTORY)
        self.backup_prefix = settings.BACKUP.PREFIX.format(PROJECT_NAME=self.project_name)
        self.vscode_paths = settings.VSCODE.PATHS
        self.logger = self.setup_logging()

    def setup_logging(self):
        # [AI]: Set up logging configuration for both file and console output
        log_dir = PROJECT_ROOT / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / settings.BACKUP_LOGS.VIEW_LOG

        logger = logging.getLogger(__name__)
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

    def get_backups(self) -> List[Path]:
        # [AI]: Retrieve and sort available backups based on modification time
        return sorted(
            [item for item in self.backup_directory.iterdir() if item.is_dir() and item.name.startswith(self.backup_prefix)],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

    def find_vscode_path(self) -> Optional[str]:
        # [AI]: Locate VSCode executable in predefined paths
        vscode_paths = [Path(os.path.expandvars(path)) for path in self.vscode_paths]
        return next((str(path) for path in vscode_paths if path.exists()), None)

    def view_backup(self, backup_path: Path):
        # [AI]: Copy selected backup to a temporary directory and open in VSCode
        print(info_message("\nStarting viewing process for:"), file_path_message(str(backup_path)))
        
        temp_dir = tempfile.mkdtemp()
        print(info_message("Created temporary directory:"), file_path_message(str(temp_dir)))
        print()  # Add an extra line for spacing
        
        try:
            # [AI]: Copy backup files to temporary directory with progress bar
            print(info_message("Copying files..."))
            for src in tqdm(list(backup_path.rglob('*')), desc="Progress", 
                            bar_format="{l_bar}{bar:20}| {n_fmt}/{total_fmt}",
                            disable=None):
                relative_path = src.relative_to(backup_path)
                dest = Path(temp_dir) / relative_path
                
                if src.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                elif src.is_file():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)

            # [AI]: Find VSCode executable and open backup in a new window
            vscode_path = self.find_vscode_path()
            if not vscode_path:
                print(error_message("VSCode executable not found in any of the expected locations."))
                return

            print(info_message("Opening backup in VSCode:"), file_path_message(str(temp_dir)))
            vscode_process = subprocess.Popen([vscode_path, temp_dir], shell=False)
            
            print(warning_message("WARNING:", "Backup is now open in VSCode. Close the VSCode window when you're done viewing."))
            print(warning_message("WARNING:", "You can also press Ctrl+C here to force close and cleanup."))
            
            # [AI]: Wait for VSCode process to exit or user interruption
            try:
                while True:
                    if not psutil.pid_exists(vscode_process.pid):
                        print(warning_message("WARNING:", "VSCode window closed. Proceeding with cleanup..."))
                        break
                    time.sleep(1)  # Check every second
            except KeyboardInterrupt:
                print(warning_message("\nWARNING:", "Operation cancelled by user. Cleaning up..."))
        finally:
            # [AI]: Clean up temporary directory with retry mechanism
            print(info_message("\nCleaning up temporary directory..."))
            for _ in range(5):  # Try to delete up to 5 times
                try:
                    shutil.rmtree(temp_dir)
                    print(success_message("Temporary directory deleted successfully."))
                    print()  # Add a line break after successful deletion
                    break
                except PermissionError:
                    print(warning_message("WARNING:", "Unable to delete temporary directory. Retrying in 2 seconds..."))
                    time.sleep(2)
            else:
                print(error_message(f"Could not delete temporary directory: {temp_dir}"))
                print(warning_message("WARNING:", "Please delete it manually when VSCode is closed."))
                print()  # Add a line break if deletion fails

        if not isinstance(sys.exc_info()[1], KeyboardInterrupt):
            print(success_message("Viewing completed for:"), file_path_message(str(backup_path)))
            print()  # Add a line break after viewing completed message

    def check_backup_directory(self):
        print()  # Add a line break before the first message
        if not self.backup_directory.exists():
            print(warning_message("WARNING:", f"Backup folder at this path does not exist: {file_path_message(str(self.backup_directory))}"))
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

    def run(self):
        # [AI]: Main method to run the backup viewer
        try:
            print(success_message("\nStarting backup viewing process"))
            
            # [AI]: Add this check for the backup directory
            if not self.check_backup_directory():
                return

            backups = self.get_backups()
            
            if not backups:
                print(warning_message("\nWARNING:", "No backups found."))
                print()  # Add a line break after the warning
                return

            # [AI]: Display available backups with modification times
            print(info_message("\nAvailable backups:"))
            for i, backup in enumerate(backups):
                mod_time = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(success_message(f"{i + 1}. {backup.name}"), f"(Modified: {mod_time})")

            # [AI]: User input loop for backup selection
            while True:
                choice = input(prompt_message("\nEnter the number of the backup to view or 'q' to quit: "))
                
                if choice.lower() == 'q':
                    print(info_message("Exiting the backup viewer."))
                    print()  # Add a line break after exiting message
                    return  # Exit the method entirely

                try:
                    index = int(choice) - 1
                    if 0 <= index < len(backups):
                        selected_backup = backups[index]
                        print(success_message("Selected backup:"), file_path_message(selected_backup.name), end='')
                        confirm = input(prompt_message(" Are you sure you want to view this backup? (y/n): "))
                        if confirm.lower() == 'y':
                            self.view_backup(selected_backup)
                            break
                        else:
                            print(warning_message("WARNING:", "Viewing cancelled."))
                    else:
                        print(error_message("Invalid backup number. Please try again."))
                except ValueError:
                    print(error_message("Invalid input. Please enter a number or 'q' to quit."))

        except KeyboardInterrupt:
            print(warning_message("\nWARNING:", "Operation cancelled by user."))
            print()  # Add a line break after the warning
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            print(error_message("\nAn unexpected error occurred. Check the logs for more details."))
            print()  # Add a line break after the error message

# [AI]: Signal handler for graceful exit on SIGINT (Ctrl+C)
def signal_handler(sig, frame):
    print(warning_message("WARNING:", "Operation cancelled by user. Cleaning up..."))
    sys.exit(0)

def main():
    # [AI]: Set up signal handler and run the BackupViewer
    signal.signal(signal.SIGINT, signal_handler)
    
    viewer = BackupViewer()
    viewer.run()

if __name__ == "__main__":
    main()