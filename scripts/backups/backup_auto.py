# [AI]: This file implements an automatic backup service for a project.
# It provides functionality to create periodic backups of the project directory.
# Key features:
# - Configurable backup intervals
# - Exclusion of specific files and directories
# - Colored console output
# - Logging of backup operations
# - Automatic termination when parent process ends

import os
import shutil
import datetime
import logging
import time
import schedule
import psutil
from pathlib import Path
from dynaconf import Dynaconf
from colorama import Fore, Style, init
from queue import Queue
import sys
import subprocess
import threading

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

# [AI]: Load settings from configuration files using Dynaconf
PROJECT_ROOT = Path(__file__).parents[2]
settings = Dynaconf(settings_files=[
    str(PROJECT_ROOT / "backend/config/settings.toml"),
    str(PROJECT_ROOT / "backend/config/settings.lcl.toml")
])

class AutoBackupService:
    # [AI]: This class implements the core functionality of the automatic backup service
    def __init__(self):
        # [AI]: Initialize service parameters from settings
        self.project_name = settings.PROJECT.NAME
        self.default_interval = settings.BACKUP.DEFAULT_INTERVAL_MINUTES
        self.exclude_content = set(settings.BACKUP.EXCLUDE_CONTENT)
        self.exclude_extensions = set(settings.BACKUP.EXCLUDE_EXTENSIONS)
        self.log_extensions = set(settings.BACKUP.LOG_EXTENSIONS)
        self.backup_prefix = settings.BACKUP.PREFIX.format(PROJECT_NAME=self.project_name)
        self.backup_directory = Path(settings.BACKUP.DIRECTORY)
        self.logger = self.setup_logging()
        self.check_backup_directory()

    # [AI]: Set up logging for the backup service
    def setup_logging(self):
        log_dir = PROJECT_ROOT / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / settings.BACKUP_LOGS.AUTO_LOG

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(settings.LOGGING.FORMAT)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)

        return logger

    # [AI]: Copy the project tree, excluding specified content and file extensions
    def copy_project_tree(self, src: Path, dest: Path):
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
                            if item.name not in self.exclude_content:
                                queue.put((item, item_dest))
                            else:
                                item_dest.mkdir(exist_ok=True)
                        else:
                            if not any(item.name.endswith(ext) for ext in self.exclude_extensions):
                                if any(item.name.endswith(ext) for ext in self.log_extensions):
                                    # [AI]: Create an empty file for log files
                                    item_dest.touch()
                                else:
                                    shutil.copy2(item, item_dest)
                else:
                    if not any(current_src.name.endswith(ext) for ext in self.exclude_extensions):
                        if any(current_src.name.endswith(ext) for ext in self.log_extensions):
                            # [AI]: Create an empty file for log files
                            current_dest.touch()
                        else:
                            shutil.copy2(current_src, current_dest)
            except Exception as e:
                self.logger.error(f"Error processing {current_src}: {str(e)}")

    # [AI]: Create a backup of the project
    def create_backup(self) -> Path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.backup_prefix}{timestamp}"
        backup_dir = self.backup_directory / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)

        print(info_message("Creating backup..."))
        try:
            self.copy_project_tree(PROJECT_ROOT, backup_dir)

            # [AI]: Copy the public directory separately
            public_src = PROJECT_ROOT / 'frontend' / 'public'
            public_dest = backup_dir / 'frontend' / 'public'
            if public_src.exists():
                shutil.copytree(public_src, public_dest, dirs_exist_ok=True)
                self.logger.debug(f"Copied public directory: {public_src} to {public_dest}")

            self.logger.info(f"Backup completed: {backup_dir}")
            return backup_dir
        except KeyboardInterrupt:
            print(warning_message("WARNING:", "Backup process interrupted by user. Cleaning up..."))
            self.logger.warning("Backup process interrupted by user")
            shutil.rmtree(backup_dir, ignore_errors=True)
            raise
        except Exception as e:
            self.logger.error(f"Error during backup creation: {str(e)}")
            shutil.rmtree(backup_dir, ignore_errors=True)
            raise

    # [AI]: Execute the backup process and handle exceptions
    def run_backup(self):
        try:
            print(info_message("Initiating backup..."))
            backup_path = self.create_backup()
            print(success_message(f"Automatic backup created: {file_path_message(str(backup_path))}"))
            self.logger.info(f"Automatic backup created: {backup_path}")
        except KeyboardInterrupt:
            print(warning_message("WARNING:", "Backup process cancelled by user"))
            self.logger.warning("Backup process cancelled by user")
        except Exception as e:
            error_msg = f"Error during automatic backup: {str(e)}"
            print(error_message(error_msg))
            self.logger.error(error_msg)

    # [AI]: Check if the parent process is still running
    @staticmethod
    def is_parent_process_running() -> bool:
        parent = psutil.Process(os.getppid())
        return parent.is_running() and parent.status() != psutil.STATUS_ZOMBIE

    # [AI]: Get the backup interval from user input or use the default
    def get_backup_interval(self) -> int:
        while True:
            user_input = input(prompt_message(f"Press Enter to accept the default backup interval of {self.default_interval} minutes, or enter a custom interval: ")).strip()
            if user_input == "":
                return self.default_interval
            try:
                interval = int(user_input)
                if interval > 0:
                    return interval
                else:
                    print(error_message("Please enter a positive integer."))
            except ValueError:
                print(error_message("Invalid input. Please enter a positive integer or press Enter for the default."))

    # [AI]: Ensure the backup directory exists
    def ensure_backup_directory_exists(self):
        print()  # Add a line break before the first message
        if not self.backup_directory.exists():
            print(warning_message("WARNING:", f"Backup directory does not exist: {file_path_message(str(self.backup_directory))}"))
            create_folder = input(prompt_message("Would you like to create the backup folder? (y/n): ")).strip().lower()
            if create_folder == 'y':
                if not self.create_backup_folder():
                    self.exit_with_message("Cannot proceed without a backup folder.")
            else:
                self.exit_with_message("Cannot proceed without a backup folder.")

    def create_backup_folder(self):
        print("Running backup folder creation script...")
        process = subprocess.Popen([sys.executable, f"{PROJECT_ROOT}/scripts/backups/backup_create_folder.py"],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        def handle_input():
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    if "Create backup folder at" in output:
                        process.stdin.write('y\n')
                        process.stdin.flush()

        thread = threading.Thread(target=handle_input)
        thread.start()

        stdout, stderr = process.communicate()
        thread.join()

        if process.returncode == 0 and "Backup folder created at:" in stdout:
            print(success_message("Backup folder created successfully."))
            return True
        else:
            print(warning_message("Backup folder creation was cancelled or failed."))
            if stderr:
                print(error_message(f"Error: {stderr.strip()}"))
            return False

    def exit_with_message(self, message):
        print(error_message(message))
        print()  # Add a line break after the last message
        sys.exit(1)

    # [AI]: Check if the backup directory exists
    def check_backup_directory(self):
        print()  # Add a line break before the first message
        if not self.backup_directory.exists():
            print(warning_message("WARNING:", f"Backup directory does not exist: {file_path_message(str(self.backup_directory))}"))
            print(prompt_message("Please create a backup folder using the following command:"))
            print(file_path_message("python scripts/backups/backup_create_folder.py"))
            print(prompt_message("Then run this script again."))
            print()  # Add a line break after the last message
            sys.exit(1)

    # [AI]: Main method to run the automatic backup service
    def run(self):
        print(success_message("Starting automatic backup service"))
        self.logger.info("Starting automatic backup service")

        # Ensure backup directory exists before proceeding
        self.ensure_backup_directory_exists()

        interval = self.get_backup_interval()
        print(info_message(f"Setting backup interval to {interval} minutes"))
        self.logger.info(f"Setting backup interval to {interval} minutes")

        schedule.every(interval).minutes.do(self.run_backup)

        self.run_backup()

        try:
            while self.is_parent_process_running():
                schedule.run_pending()
                time.sleep(settings.BACKUP.MAIN_LOOP_SLEEP_SECONDS)
        except KeyboardInterrupt:
            print(warning_message("WARNING:", "Automatic backup service stopped by user"))
            self.logger.info("Automatic backup service stopped by user")
        except Exception as e:
            error_msg = f"Unexpected error in main loop: {str(e)}"
            print(error_message(error_msg))
            self.logger.error(error_msg)
        finally:
            print(success_message("Automatic backup service stopped"))
            self.logger.info("Automatic backup service stopped")

# [AI]: Main entry point of the script
def main():
    try:
        auto_backup_service = AutoBackupService()
        auto_backup_service.run()
    except SystemExit:
        pass  # SystemExit has already been handled
    except Exception as e:
        print(error_message(f"An unexpected error occurred: {str(e)}"))
        print()  # Add a line break after the last message

if __name__ == "__main__":
    main()