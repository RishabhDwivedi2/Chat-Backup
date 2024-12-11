# [AI]: This file implements the creation of a backup folder for a project.
# It provides functionality to determine the project root, create a backup folder,
# and update the project settings with the new backup directory path.
# Key features:
# - Determine the project root directory
# - Create a backup folder with user confirmation
# - Update project settings with the backup directory path
# - Colorized console output for better user experience
# - Error handling and user input validation

import toml
from pathlib import Path
from dynaconf import Dynaconf
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

def prompt_message(message: str) -> str:
    return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"

def file_path_message(message: str) -> str:
    return f"{Fore.WHITE}{message}{Style.RESET_ALL}"

# [AI]: Load settings from configuration files using Dynaconf
PROJECT_ROOT = Path(__file__).parents[2]
settings = Dynaconf(settings_files=[
    str(PROJECT_ROOT / "backend/config/settings.toml"),
    str(PROJECT_ROOT / "backend/config/settings.lcl.toml")
])

class BackupFolderCreator:
    # [AI]: Initialize the class with project-specific settings
    def __init__(self):
        self.project_name = settings.PROJECT.NAME
        self.backup_suffix = settings.BACKUP.FOLDER_SUFFIX
        self.root_identifier = settings.PROJECT.ROOT_IDENTIFIER

    # [AI]: Determine the project root directory by searching for a specific file
    def get_project_root(self):
        current_dir = PROJECT_ROOT
        while not (current_dir / self.root_identifier).is_file():
            current_dir = current_dir.parent
            if current_dir == current_dir.parent:
                raise FileNotFoundError("Project root not found")
        return current_dir

    # [AI]: Create a backup folder with user interaction and confirmation
    def create_backup_folder(self):
        project_root = self.get_project_root()
        parent_dir = project_root.parent
        default_backup_dir = parent_dir / f"{self.project_name}{self.backup_suffix}"

        print(info_message(f"Project root: {file_path_message(str(project_root))}"))
        print(info_message(f"Suggested backup folder: {file_path_message(str(default_backup_dir))}"))

        # [AI]: Check if the default backup folder already exists
        if default_backup_dir.exists():
            print(warning_message("WARNING:", f"Backup folder already exists at {file_path_message(str(default_backup_dir))}."))
            return str(default_backup_dir)

        # [AI]: User interaction loop for backup folder creation
        while True:
            prompt = f"Create backup folder at {file_path_message(str(default_backup_dir))}?"
            options = "(Y/n/q to quit): "
            create_prompt = prompt_message(f"{prompt} {options}")
            user_input = input(create_prompt).strip().lower()
            
            if user_input == 'q':
                print(warning_message("WARNING:", "Process cancelled by user."))
                return None
            elif user_input == '' or user_input == 'y':
                backup_dir = default_backup_dir
                break
            elif user_input == 'n':
                custom_prompt = prompt_message("Enter custom backup folder path (or 'q' to quit): ")
                custom_path = input(custom_prompt).strip()
                if custom_path.lower() == 'q':
                    print(warning_message("WARNING:", "Process cancelled by user."))
                    return None
                backup_dir = Path(custom_path).resolve()
                confirm_prompt = prompt_message(f"Confirm creating backup folder at {file_path_message(str(backup_dir))}? (Y/n): ")
                confirm = input(confirm_prompt).strip().lower()
                if confirm == '' or confirm == 'y':
                    break
            else:
                print(error_message("Invalid input. Please try again."))

        # [AI]: Create the backup folder and handle potential errors
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            print(success_message(f"Backup folder created at: {file_path_message(str(backup_dir))}"))
        except Exception as e:
            print(error_message(f"Error creating backup folder: {e}"))
            return None

        return str(backup_dir)

    # [AI]: Update the project settings with the new backup directory path
    def update_settings(self, backup_dir):
        settings_file = PROJECT_ROOT / 'backend' / 'config' / 'settings.lcl.toml'

        if settings_file.exists():
            print(info_message(f"Updating settings file: {file_path_message(str(settings_file))}"))
            
            # [AI]: Load existing settings from the TOML file
            with open(settings_file, 'r') as f:
                current_settings = toml.load(f)
            
            # [AI]: Ensure the BACKUP section exists in the settings
            if 'BACKUP' not in current_settings:
                current_settings['BACKUP'] = {}
            
            # [AI]: Update the backup directory path if it's different
            if current_settings['BACKUP'].get('DIRECTORY') == backup_dir:
                print(warning_message("WARNING:", f"File {file_path_message(str(settings_file))} already contains the correct backup directory path."))
            else:
                current_settings['BACKUP']['DIRECTORY'] = backup_dir
                with open(settings_file, 'w') as f:
                    toml.dump(current_settings, f)
                print(success_message(f"Updated {file_path_message(str(settings_file))} with new backup directory path: {file_path_message(backup_dir)}"))
        else:
            print(error_message(f"File {file_path_message(str(settings_file))} does not exist. Unable to update backup directory path."))

    # [AI]: Main method to orchestrate the backup folder creation process
    def run(self):
        print(success_message("\nStarting backup folder creation process"))

        backup_dir = self.create_backup_folder()
        if backup_dir:
            self.update_settings(backup_dir)
        else:
            print(warning_message("WARNING:", "Backup folder creation cancelled. Settings not updated."))

        print(success_message("Backup folder creation process completed"))
        print()  # Add a single line break after the last message

# [AI]: Entry point of the script
def main():
    backup_folder_creator = BackupFolderCreator()
    backup_folder_creator.run()

if __name__ == "__main__":
    main()
