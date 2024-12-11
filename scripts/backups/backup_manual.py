# [AI]: This file implements a manual backup system for a project.
# It provides functionality to create backups, copy project trees, and run update scripts.
# Key features:
# - Colored console output for better user experience
# - Logging of backup operations
# - Exclusion of specific files and directories from backup
# - Running of update scripts before backup
# - User input for custom backup names
# - Error handling and cleanup on failure

import os
import shutil
import datetime
import logging
import subprocess
import sys
from pathlib import Path
from dynaconf import Dynaconf
from queue import Queue
from colorama import Fore, Style, init

# [AI]: Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# [AI]: Define color constants for different types of messages
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

# [AI]: Load settings from configuration files
PROJECT_ROOT = Path(__file__).parents[2]
settings = Dynaconf(settings_files=[
    str(PROJECT_ROOT / "backend/config/settings.toml"),
    str(PROJECT_ROOT / "backend/config/settings.lcl.toml")
])
PROJECT_NAME = settings.PROJECT.NAME
EXCLUDE_CONTENT = set(settings.BACKUP.EXCLUDE_CONTENT)
EXCLUDE_EXTENSIONS = set(settings.BACKUP.EXCLUDE_EXTENSIONS)
LOG_EXTENSIONS = set(settings.BACKUP.LOG_EXTENSIONS)

# [AI]: Set up logging for the backup process
def setup_logging():
    log_dir = PROJECT_ROOT / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / settings.BACKUP_LOGS.MANUAL_LOG

    # [AI]: Create a logger that doesn't propagate to the root logger
    logger = logging.getLogger(__name__)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter(settings.LOGGING.FORMAT)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    return logger

# [AI]: Copy the project tree, excluding specified content and file extensions
def copy_project_tree(src: Path, dest: Path):
    queue = Queue()
    queue.put((src, dest))

    while not queue.empty():
        current_src, current_dest = queue.get()
        try:
            if current_src.is_dir():
                current_dest.mkdir(exist_ok=True)
                for item in current_src.iterdir():
                    item_dest = current_dest / item.name
                    if item.is_dir():
                        if item.name not in EXCLUDE_CONTENT:
                            queue.put((item, item_dest))
                        else:
                            item_dest.mkdir(exist_ok=True)
                    else:
                        if not any(item.name.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                            if any(item.name.endswith(ext) for ext in LOG_EXTENSIONS):
                                # [AI]: Create an empty file for log files
                                item_dest.touch()
                            else:
                                shutil.copy2(item, item_dest)
            else:
                if not any(current_src.name.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                    if any(current_src.name.endswith(ext) for ext in LOG_EXTENSIONS):
                        # [AI]: Create an empty file for log files
                        current_dest.touch()
                    else:
                        shutil.copy2(current_src, current_dest)
        except Exception as e:
            logging.error(f"Error processing {current_src}: {str(e)}")

# [AI]: Run the update_all.py script before creating the backup
def run_update_all():
    script_path = PROJECT_ROOT / "scripts" / "updates" / "update_all.py"
    logging.info(f"Running update_all.py")
    print(info_message("Running update_all.py..."))
    
    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        logging.info("update_all.py completed successfully")
        print(success_message("update_all.py completed successfully"))
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running update_all.py: {e}")
        print(error_message(f"Error running update_all.py: {e}"))
        raise

# [AI]: Create a backup of the project
def create_backup():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{settings.BACKUP.PREFIX.format(PROJECT_NAME=PROJECT_NAME)}{timestamp}"
    
    # [AI]: Prompt user for a custom backup name
    while True:
        user_input = input(prompt_message("Enter a name for this manual backup:")).strip()
        if user_input:
            backup_name += f"_{user_input}"
            break
        else:
            print(error_message("Backup name cannot be empty. Please enter a valid name."))
    
    backup_dir = Path(settings.BACKUP.DIRECTORY) / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)

    print(info_message("Creating backup..."))
    try:
        copy_project_tree(PROJECT_ROOT, backup_dir)

        # [AI]: Copy the public directory separately
        public_src = PROJECT_ROOT / 'frontend' / 'public'
        public_dest = backup_dir / 'frontend' / 'public'
        if public_src.exists():
            shutil.copytree(public_src, public_dest, dirs_exist_ok=True)
            logging.debug(f"Copied public directory: {public_src} to {public_dest}")

        logging.info(f"Backup completed: {backup_dir}")
        return backup_dir
    except KeyboardInterrupt:
        print(warning_message("\nWARNING:", "Backup process interrupted by user. Cleaning up..."))
        logging.warning("Backup process interrupted by user")
        shutil.rmtree(backup_dir, ignore_errors=True)
        raise
    except Exception as e:
        logging.error(f"Error during backup creation: {str(e)}")
        print(error_message(f"Error during backup creation: {str(e)}"))
        shutil.rmtree(backup_dir, ignore_errors=True)
        raise

# [AI]: Add this new function to check for the backup directory
def check_backup_directory():
    backup_directory = Path(settings.BACKUP.DIRECTORY)
    print()  # Add a line break before the first message
    if not backup_directory.exists():
        print(warning_message("WARNING:", f"Backup directory does not exist: {file_path_message(str(backup_directory))}"))
        print(prompt_message("Please create a backup folder using the following command:"))
        print(file_path_message("python scripts/backups/backup_create_folder.py"))
        print(prompt_message("Then run this script again."))
        print()  # Add a line break after the last message
        sys.exit(1)

# [AI]: Main function to orchestrate the backup process
def main():
    try:
        logger = setup_logging()
        logger.info("Starting manual backup process")
        print(success_message("\nStarting manual backup process"))
        
        # [AI]: Add this line to check for the backup directory
        check_backup_directory()
        
        try:
            run_update_all()
        except subprocess.CalledProcessError:
            logger.error("Backup process failed due to error in update_all.py")
            print(error_message("Backup process failed due to error in update_all.py"))
            sys.exit(1)
        
        backup_path = create_backup()
        
        if backup_path:
            logger.info(f"Backup created at: {backup_path} Manual backup process completed successfully.")
            print(success_message(f"Backup created at: {file_path_message(str(backup_path))}"))
            print(success_message("Manual backup process completed successfully."))
            print()  # [AI]: Add an extra line after the success message
        else:
            logger.warning("Backup process completed, but no files were backed up. Please check your settings.")
            print(warning_message("WARNING:", "Backup process completed, but no files were backed up. Please check your settings."))
            print()  # [AI]: Add an extra line after the warning message

    except KeyboardInterrupt:
        logger.info("Manual backup process stopped by user")
        print(warning_message("WARNING:", "Manual backup process stopped by user"))
        print()  # [AI]: Add an extra line after the warning message
    except Exception as e:
        logger.error(f"Unexpected error in main process: {str(e)}")
        print(error_message(f"Unexpected error in main process: {str(e)}"))
        print()  # [AI]: Add an extra line after the error message

if __name__ == "__main__":
    main()