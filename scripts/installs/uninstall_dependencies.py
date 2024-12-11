# [AI]: This file implements a package uninstallation utility for Python and Node.js projects.
# It provides functionality to uninstall pip and npm packages from a project.
# Key features:
# - Detects project root directory
# - Checks for Python and npm installations
# - Supports uninstallation of multiple packages in one command
# - Updates requirements.txt and package.json files
# - Provides colored console output for better readability
# - Displays a spinner during package uninstallation

import subprocess
import sys
from pathlib import Path
import logging
import json
import re
import os
import shutil
import threading
import itertools
import time
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
    return format_message(message, PROMPT_COLOR)

def file_path_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

# [AI]: Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Function to find the project root directory
def find_project_root():
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / "requirements.txt").exists() or (current_dir / "package.json").exists():
            return current_dir
        current_dir = current_dir.parent
    return Path.cwd()  # If no project root found, use current directory

PROJECT_ROOT = find_project_root()

# [AI]: Function to check Python and npm installations
def check_python_and_npm():
    print()  # Add a line space before Python version
    python_version = get_python_version()
    npm_version = get_npm_version()

    if python_version:
        print(info_message(f"Python is installed and accessible (version: {python_version})"))
    else:
        print(error_message("Python is not installed or not accessible."))

    if npm_version:
        print(info_message(f"npm is installed and accessible (version: {npm_version})"))
    else:
        print(error_message("npm is not installed or not accessible."))

    return python_version is not None

# [AI]: Function to get Python version
def get_python_version():
    try:
        result = subprocess.run([sys.executable, "--version"], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

# [AI]: Function to get npm version
def get_npm_version():
    npm_path = get_npm_path()
    if npm_path:
        try:
            result = subprocess.run([npm_path, "--version"], check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    return None

# [AI]: Function to get npm executable path
def get_npm_path():
    npm_cmd = 'npm.cmd' if sys.platform.startswith('win') else 'npm'
    npm_path = shutil.which(npm_cmd)
    if npm_path is None:
        logger.error("npm is not found in the system PATH. Please ensure Node.js and npm are installed correctly.")
    return npm_path

# [AI]: Function to get Python executable path in virtual environment
def get_venv_python(venv_path):
    venv_path = Path(venv_path)
    return venv_path / "Scripts" / "python.exe" if sys.platform.startswith('win') else venv_path / "bin" / "python"

# [AI]: Function to find a file in the project directory
def find_file(filename, start_path='.'):
    for root, dirs, files in os.walk(start_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

# [AI]: Function to get user input for package uninstallation
def get_package_input():
    print(prompt_message("\nEnter package name(s) to uninstall. For multiple packages, separate with spaces."))
    print(prompt_message("For pip packages, use 'pip uninstall package1 package2 ...'"))
    print(prompt_message("For npm packages, use 'npm uninstall package1 package2 ...'"))
    user_input = input(prompt_message("Packages to uninstall: "))
    packages = []
    
    splits = re.split(r'(npm uninstall|pip uninstall)', user_input)
    
    current_type = None
    for split in splits:
        split = split.strip()
        if split == 'npm uninstall':
            current_type = 'npm'
        elif split == 'pip uninstall':
            current_type = 'pip'
        elif split:
            if current_type:
                # Split the package names if there are multiple
                for package in split.split():
                    packages.append((current_type, package))
            else:
                # If no type specified, assume it's a pip package
                packages.append(('pip', split))
    
    return packages

# [AI]: Spinner class for displaying progress during package uninstallation
class Spinner:
    def __init__(self, message=''):
        self.message = info_message(message)
        self.spinning = False
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])

    def spin(self):
        while self.spinning:
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

    def start(self):
        self.spinning = True
        threading.Thread(target=self.spin).start()

    def stop(self):
        self.spinning = False

# [AI]: Function to uninstall a Python package
def uninstall_python_package(venv_path, package):
    venv_python = get_venv_python(venv_path)
    print()  # Add a line space before the Uninstalling message
    spinner = Spinner(f'Uninstalling {package}')
    spinner.start()
    try:
        subprocess.run([str(venv_python), "-m", "pip", "uninstall", "-y", package], check=True, capture_output=True)
        spinner.stop()
        print(success_message(f"\nSuccessfully uninstalled {package}"))
        return True
    except subprocess.CalledProcessError as e:
        spinner.stop()
        print(error_message(f"\nError uninstalling {package}: {e}"))
        return False

# [AI]: Function to uninstall a Node.js package
def uninstall_node_package(package, package_json_path):
    npm_path = get_npm_path()
    if not npm_path:
        print(error_message("\nnpm is not installed or not accessible. Cannot uninstall Node packages."))
        return False

    install_dir = package_json_path.parent
    print()  # Add a line space before the Uninstalling message
    spinner = Spinner(f'Uninstalling {package}')
    spinner.start()
    try:
        subprocess.run([npm_path, "uninstall", package, "--prefix", str(install_dir)], check=True, capture_output=True)
        spinner.stop()
        print(success_message(f"\nSuccessfully uninstalled {package}"))
        return True
    except subprocess.CalledProcessError as e:
        spinner.stop()
        print(error_message(f"\nError uninstalling {package}: {e}"))
        return False

# [AI]: Function to update requirements.txt after uninstalling a Python package
def update_requirements_txt(package):
    requirements_path = find_file('requirements.txt')
    if not requirements_path:
        print(error_message("\nrequirements.txt not found in the project"))
        return

    try:
        with open(requirements_path, 'r') as file:
            lines = file.readlines()

        # Remove the package from requirements.txt
        lines = [line for line in lines if not line.strip().startswith(f"{package}==")]

        with open(requirements_path, 'w') as file:
            file.writelines(lines)

        print(success_message(f"Removed {package} from {file_path_message(requirements_path)}"))
    except Exception as e:
        print(error_message(f"Error updating {requirements_path}: {str(e)}"))

# [AI]: Function to update package.json after uninstalling a Node.js package
def update_package_json(package_json_path, package):
    try:
        with package_json_path.open('r+') as file:
            data = json.load(file)
            
            # Remove the package from dependencies and devDependencies
            if 'dependencies' in data and package in data['dependencies']:
                del data['dependencies'][package]
            if 'devDependencies' in data and package in data['devDependencies']:
                del data['devDependencies'][package]

            # Write the updated JSON back to the file
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        print(success_message(f"Removed {package} from {file_path_message(package_json_path)}"))
    except Exception as e:
        print(error_message(f"Error updating {package_json_path}: {str(e)}"))

# [AI]: Function to find package.json file in the project
def find_package_json():
    for root, _, files in os.walk(PROJECT_ROOT):
        if 'package.json' in files:
            return Path(root) / 'package.json'
    return None

# [AI]: Main function to orchestrate the uninstallation process
def main():
    if not check_python_and_npm():
        return 1

    venv_path = PROJECT_ROOT / "venv"
    venv_python = get_venv_python(venv_path)

    packages = get_package_input()
    
    if not packages:
        print(warning_message("\nWARNING:", "No packages entered. Nothing to uninstall."))
        return 0

    uninstalled_packages = []

    package_json_path = find_package_json()
    if not package_json_path:
        print(error_message("\nNo package.json found in the project. Cannot uninstall npm packages."))
    
    npm_path = get_npm_path()
    if not npm_path:
        print(error_message("\nnpm is not installed or not accessible. Cannot uninstall npm packages."))

    for prefix, package_name in packages:
        if prefix == 'npm':
            if package_json_path and npm_path:
                if uninstall_node_package(package_name, package_json_path):
                    update_package_json(package_json_path, package_name)
                    uninstalled_packages.append(f"npm:{package_name}")
        elif prefix == 'pip':
            if uninstall_python_package(venv_path, package_name):
                update_requirements_txt(package_name)
                uninstalled_packages.append(f"pip:{package_name}")

    if uninstalled_packages:
        print(info_message("\nSummary of uninstalled packages:"))
        for package in uninstalled_packages:
            print(info_message(f"- {package}"))
    else:
        print(warning_message("\nWARNING:", "No packages were uninstalled."))

    print()  # Add an extra line break at the end
    return 0

if __name__ == "__main__":
    sys.exit(main())