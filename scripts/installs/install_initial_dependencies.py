# [AI]: This file implements an automated dependency installation process for Python and Node.js projects.
# It provides functionality to set up virtual environments, install Python packages, and install Node.js packages.
# Key features:
# - Cross-platform compatibility (Windows and Unix-like systems)
# - Virtual environment creation for Python
# - Progress tracking for package installations
# - Colored console output for better readability
# - Automatic package.json and settings.lcl.toml updates
# - Error handling and logging

import subprocess
import sys
from pathlib import Path
import logging
import os
import time
import shutil
import venv
import json
import itertools
import threading
from colorama import Fore, Style, init
from typing import List, Optional

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

# [AI]: Check if Python is installed and accessible
def check_python():
    try:
        subprocess.run([sys.executable, "--version"], check=True, capture_output=True)
        print(success_message("\nPython is installed and accessible."))
        return True
    except subprocess.CalledProcessError:
        print(error_message("\nPython is not installed or not accessible."))
        return False

# [AI]: Get the path to the npm executable, considering different platforms and common installation locations
def get_npm_path():
    npm_cmd = 'npm.cmd' if sys.platform.startswith('win') else 'npm'
    npm_path = shutil.which(npm_cmd)
    
    if npm_path:
        try:
            subprocess.run([npm_path, "--version"], check=True, capture_output=True)
            return npm_path
        except subprocess.CalledProcessError:
            pass
    
    # [AI]: Check common npm locations on Windows
    if sys.platform.startswith('win'):
        common_locations = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expandvars(r"%APPDATA%\npm\npm.cmd")
        ]
        
        for location in common_locations:
            if os.path.exists(location):
                try:
                    subprocess.run([location, "--version"], check=True, capture_output=True)
                    return location
                except subprocess.CalledProcessError:
                    pass
    
    return None

# [AI]: Create a virtual environment if it doesn't exist
def create_venv(venv_path):
    venv_path = Path(venv_path)
    if not venv_path.exists():
        print(info_message(f"Creating virtual environment at {file_path_message(str(venv_path))}"))
        venv.create(venv_path, with_pip=True)
    else:
        print(info_message(f"Virtual environment already exists at {file_path_message(str(venv_path))}"))

# [AI]: Get the path to the Python executable in the virtual environment
def get_venv_python(venv_path):
    venv_path = Path(venv_path)
    return venv_path / "Scripts" / "python.exe" if sys.platform.startswith('win') else venv_path / "bin" / "python"

# [AI]: Find a file by name in the current directory or its subdirectories
def find_file(filename, search_path=None):
    if search_path is None:
        search_path = Path.cwd()
    for root, _, files in os.walk(search_path):
        if filename in files:
            return Path(root) / filename
    return None

# [AI]: Install Python dependencies from requirements.txt
def install_python_deps(venv_path):
    requirements_file = find_file("requirements.txt")
    if not requirements_file:
        print(error_message("requirements.txt not found in the project directory."))
        return False

    create_venv(venv_path)
    venv_python = get_venv_python(venv_path)
    if not venv_python.exists():
        print(error_message(f"Virtual environment Python not found at {venv_python}"))
        return False

    print(info_message(f"Using Python from virtual environment: {file_path_message(str(venv_python))}"))
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    total_packages = len(requirements)
    print(info_message(f"Installing {total_packages} Python packages..."))

    start_time = time.time()
    for i, package in enumerate(requirements, 1):
        try:
            subprocess.run([str(venv_python), "-m", "pip", "install", package], check=True, capture_output=True, timeout=300)
            progress = i / total_packages
            bar_length = 50
            filled_length = int(bar_length * progress)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / progress
            time_left = estimated_total_time - elapsed_time
            print(f"\r{info_message(f'[{bar}] {i}/{total_packages} ({progress:.1%}) - ETA: {time_left:.0f}s')}", end='', flush=True)
        except subprocess.CalledProcessError as e:
            print(error_message(f"\nError installing {package}: {e}"))
            return False
        except subprocess.TimeoutExpired:
            print(error_message(f"\nTimeout while installing {package}. The package may be too large or the network connection is slow."))
            return False
        except KeyboardInterrupt:
            print(warning_message("\nWARNING:", "Installation process interrupted by user."))
            return False

    print(success_message("\nAll Python packages installed successfully."))
    return True

# [AI]: Spinner animation for Node.js package installation
def spinner_task(stop_event):
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while not stop_event.is_set():
        print(f"\r{info_message('Installing Node.js packages...')} {next(spinner)}", end='', flush=True)
        time.sleep(0.1)

# [AI]: Install Node.js dependencies using npm
def install_node_deps():
    package_json = find_file("package.json")
    if not package_json:
        print(error_message("package.json not found in the project directory."))
        return False

    npm_path = get_npm_path()
    if not npm_path:
        print(error_message("Npm is not installed or not accessible."))
        return False

    try:
        os.chdir(package_json.parent)
        
        print(info_message("Starting Node.js package installation..."))
        
        command = [npm_path, "install"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # [AI]: Start spinner animation in a separate thread
        stop_event = threading.Event()
        spinner_thread = threading.Thread(target=spinner_task, args=(stop_event,))
        spinner_thread.start()
        
        stdout, stderr = process.communicate()
        
        # [AI]: Stop spinner animation
        stop_event.set()
        spinner_thread.join()
        print("\r", end='', flush=True)  # Clear the spinner line
        
        if process.returncode != 0:
            print(error_message(f"\nnpm install failed with return code {process.returncode}"))
            print(error_message(f"Error output: {stderr}"))
            raise subprocess.CalledProcessError(process.returncode, command, output=stderr)
        
        print(success_message("Node.js package installation completed successfully."))
        return True
    except subprocess.CalledProcessError as e:
        print(error_message(f"\nError during Node.js package installation. Command '{e.cmd}' returned non-zero exit status {e.returncode}."))
        print(error_message(f"Error output: {e.output}"))
        return False
    except Exception as e:
        print(error_message(f"\nUnexpected error during Node.js package installation: {e}"))
        return False
    finally:
        os.chdir(Path.cwd())

# [AI]: Update package.json name and settings.lcl.toml with the project name
def update_package_json_name():
    package_json = find_file("package.json")
    if not package_json:
        print(warning_message("WARNING:", "package.json not found. Skipping package name update."))
        return

    # [AI]: Get the project name from the root directory
    root_dir = package_json.parent.parent
    project_name = root_dir.name.lower()

    # [AI]: Update package.json
    try:
        with package_json.open("r") as f:
            package_data = json.load(f)

        old_name = package_data.get("name", "")
        new_name = f"{project_name}-frontend"
        
        if old_name != new_name:
            package_data["name"] = new_name
            with package_json.open("w") as f:
                json.dump(package_data, f, indent=2)
            print(info_message(f"\nUpdated package.json name from '{old_name}' to '{new_name}'"))
        else:
            print(info_message("\npackage.json name is already up to date."))

    except json.JSONDecodeError:
        print(error_message("Error parsing package.json. It may be malformed."))
    except IOError as e:
        print(error_message(f"Error reading or writing package.json: {e}"))

    # [AI]: Update settings.lcl.toml
    settings_file = root_dir / "backend" / "config" / "settings.lcl.toml"
    try:
        # Read the TOML file
        with settings_file.open("r") as f:
            settings_content = f.read()

        # [AI]: Simple TOML parsing and updating
        updated_lines = []
        in_project_section = False
        project_name_updated = False
        for line in settings_content.splitlines():
            if line.strip() == "[PROJECT]":
                in_project_section = True
                updated_lines.append(line)
            elif in_project_section and line.strip().startswith("NAME"):
                updated_lines.append(f'NAME = "{project_name}"')
                project_name_updated = True
            else:
                updated_lines.append(line)
                if line.strip() and in_project_section:
                    in_project_section = False

        # [AI]: If NAME wasn't found in the PROJECT section, add it
        if in_project_section and not project_name_updated:
            updated_lines.append(f'NAME = "{project_name}"')

        # Write the updated content back to the file
        with settings_file.open("w") as f:
            f.write("\n".join(updated_lines))
        
        print(info_message(f"Updated settings.lcl.toml with project name: {project_name}"))
    except FileNotFoundError:
        print(error_message("settings.lcl.toml not found. Make sure it exists in the backend/config directory."))
    except Exception as e:
        print(error_message(f"Error updating settings.lcl.toml: {e}"))

# [AI]: Main function to orchestrate the dependency installation process
def main():
    try:
        if not check_python():
            return 1

        print(info_message("Starting dependency installation process..."))
        venv_path = Path.cwd() / "venv"
        
        requirements_file = find_file("requirements.txt")
        package_json = find_file("package.json")
        
        if not requirements_file and not package_json:
            print(error_message("Neither requirements.txt nor package.json found in the project directory."))
            return 1
        
        success = True
        
        if requirements_file:
            try:
                if not install_python_deps(venv_path):
                    success = False
            except Exception as e:
                print(error_message(f"An error occurred during Python dependency installation: {e}"))
                success = False
        else:
            print(warning_message("WARNING:", "requirements.txt not found. Skipping Python dependency installation."))
        
        if package_json:
            try:
                update_package_json_name()
                if not install_node_deps():
                    success = False
            except Exception as e:
                print(error_message(f"An error occurred during Node.js dependency installation: {e}"))
                success = False
        else:
            print(warning_message("WARNING:", "package.json not found. Skipping Node.js dependency installation."))
        
        if success:
            print(success_message("\nAll found dependencies installed successfully."))
            print()  # Add an extra line break here
            return 0
        else:
            print(error_message("\nDependency installation process completed with errors."))
            print()  # Add an extra line break here
            return 1
    except KeyboardInterrupt:
        print(warning_message("\nWARNING:", "Installation process interrupted by user."))
        print()  # Add an extra line break here
        return 1

if __name__ == "__main__":
    sys.exit(main())