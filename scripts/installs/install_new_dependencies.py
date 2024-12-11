# [AI]: This file implements a dependency installation system for Python and Node.js projects.
# It provides functionality to install packages, update requirement files, and manage virtual environments.
# Key features:
# - Automatic project root detection
# - Virtual environment creation and management
# - Installation of both pip and npm packages
# - Updating of requirements.txt and package.json files
# - Colored console output for better readability
# - Logging of installation process
# - Spinner animation for long-running processes

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

# [AI]: Configure logging to write to a file instead of console
logging.basicConfig(filename='install_dependencies.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Function to find the root directory of the project
def find_project_root():
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / "requirements.txt").exists() or (current_dir / "package.json").exists():
            return current_dir
        current_dir = current_dir.parent
    return Path.cwd()  # If no project root found, use current directory

PROJECT_ROOT = find_project_root()

# [AI]: Functions to get Python and npm versions
def get_python_version():
    try:
        result = subprocess.run([sys.executable, "--version"], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_npm_version():
    npm_path = get_npm_path()
    if npm_path:
        try:
            result = subprocess.run([npm_path, "--version"], check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    return None

# [AI]: Function to check if Python and npm are installed and accessible
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

# [AI]: Function to get the path to the npm executable
def get_npm_path():
    npm_cmd = 'npm.cmd' if sys.platform.startswith('win') else 'npm'
    npm_path = shutil.which(npm_cmd)
    if npm_path is None:
        logger.error("npm is not found in the system PATH. Please ensure Node.js and npm are installed correctly.")
    return npm_path

# [AI]: Function to create a virtual environment
def create_venv(venv_path):
    venv_path = Path(venv_path)
    if not venv_path.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    else:
        logger.debug(f"Virtual environment already exists at {venv_path}")

# [AI]: Function to get the path to the Python executable in the virtual environment
def get_venv_python(venv_path):
    venv_path = Path(venv_path)
    return venv_path / "Scripts" / "python.exe" if sys.platform.startswith('win') else venv_path / "bin" / "python"

# [AI]: Function to find a file in the project directory
def find_file(filename, start_dir=PROJECT_ROOT, max_depth=5):
    start_dir = Path(start_dir)
    for root, dirs, files in os.walk(str(start_dir)):
        if filename in files:
            return Path(os.path.join(root, filename))
        if len(Path(root).relative_to(start_dir).parts) >= max_depth:
            del dirs[:]
    return None

# [AI]: Function to get package input from the user
def get_package_input():
    print(prompt_message("\nEnter package name(s) to install. For multiple packages, separate with spaces."))
    print(prompt_message("For pip packages, use 'pip install package1 package2 ...'"))
    print(prompt_message("For npm packages, use 'npm install package1 package2 ...'"))
    user_input = input(prompt_message("Packages to install: "))
    packages = []
    
    # Split by 'npm install' and 'pip install' to handle both types correctly
    splits = re.split(r'(npm install|pip install)', user_input)
    
    current_type = None
    for split in splits:
        split = split.strip()
        if split == 'npm install':
            current_type = 'npm'
        elif split == 'pip install':
            current_type = 'pip'
        elif split:
            if current_type:
                # Split multiple packages and add them individually
                for package in split.split():
                    packages.append((current_type, package))
            else:
                # If no type specified, assume they're pip packages
                for package in split.split():
                    packages.append(('pip', package))
    
    return packages

# [AI]: Class to create a spinning animation for long-running processes
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

# [AI]: Function to install a Python package
def install_python_package(venv_path, package):
    venv_python = get_venv_python(venv_path)
    print()  # Add a line space before the Installing message
    spinner = Spinner(f'Installing {package}')
    spinner.start()
    try:
        subprocess.run([str(venv_python), "-m", "pip", "install", package], check=True, capture_output=True)
        spinner.stop()
        print(success_message(f"\nSuccessfully installed {package}"))
        return True
    except subprocess.CalledProcessError as e:
        spinner.stop()
        print(error_message(f"\nError installing {package}: {e}"))
        return False

# [AI]: Function to find the package.json file
def find_package_json():
    logging.info("Searching for package.json file...")
    for root, _, files in os.walk(PROJECT_ROOT):
        if 'package.json' in files:
            package_json_path = Path(root) / 'package.json'
            logging.info(f"Found package.json at: {package_json_path}")
            return package_json_path
    logging.warning("No package.json file found in the project.")
    return None

# [AI]: Function to create a simple spinner animation
def simple_spinner():
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while True:
        yield next(spinner)

# [AI]: Function to install a Node.js package
def install_node_package(package_name, package_json_path):
    npm_path = get_npm_path()
    if not npm_path:
        logging.error("npm not found. Cannot install Node.js package.")
        return False

    install_dir = package_json_path.parent
    command = [npm_path, "install", package_name, "--prefix", str(install_dir)]
    
    logging.info(f"Installing {package_name} in {install_dir}...")
    spinner = simple_spinner()
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while process.poll() is None:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')
        stdout, stderr = process.communicate()
        sys.stdout.write(' \r')
        sys.stdout.flush()
        if process.returncode == 0:
            logging.info(f"Successfully installed {package_name}")
            return True
        else:
            logging.error(f"Failed to install {package_name}: {stderr}")
            return False
    except Exception as e:
        logging.error(f"An error occurred while installing {package_name}: {str(e)}")
        return False

# [AI]: Function to get the version of an installed Node.js package
def get_node_package_version(package, package_json_path):
    logging.info(f"Determining version for {package}...")
    npm_path = get_npm_path()
    if not npm_path:
        logging.error("npm not found. Cannot determine package version.")
        return None

    try:
        # First, try using npm list
        result = subprocess.run([npm_path, "list", package, "--depth=0", "--json"], 
                                capture_output=True, text=True, check=True,
                                cwd=package_json_path.parent)
        data = json.loads(result.stdout)
        version = data.get("dependencies", {}).get(package, {}).get("version")
        if version:
            logging.info(f"Version for {package}: {version}")
            return version
    except subprocess.CalledProcessError:
        logging.warning(f"Could not determine version for {package} using npm list. Checking package.json...")
    except json.JSONDecodeError:
        logging.warning(f"Error parsing npm output for {package}. Checking package.json...")

    # If npm list fails, check package.json directly
    try:
        with package_json_path.open('r') as file:
            data = json.load(file)
        version = data.get("dependencies", {}).get(package) or data.get("devDependencies", {}).get(package)
        if version:
            logging.info(f"Version for {package} found in package.json: {version}")
            return version
        else:
            logging.warning(f"Could not find version for {package} in package.json")
            return None
    except Exception as e:
        logging.error(f"Error reading package.json: {str(e)}")
        return None

# [AI]: Function to update package.json with newly installed package
def update_package_json(package_json_path, package, is_dev):
    version = get_node_package_version(package, package_json_path)
    if not version:
        logging.warning(f"Could not determine version for {package}. package.json may already be up to date.")
        return

    logging.info(f"Updating {package_json_path} with {package}@{version}...")
    try:
        with package_json_path.open('r+') as file:
            data = json.load(file)
            
            # Ensure the required sections exist
            if 'dependencies' not in data:
                data['dependencies'] = {}
            if 'devDependencies' not in data:
                data['devDependencies'] = {}

            # Determine the target section
            target = data['devDependencies'] if is_dev else data['dependencies']

            # Update or add the package
            if package not in target or target[package] != version:
                target[package] = version
                
                # Sort the dependencies alphabetically
                sorted_deps = dict(sorted(target.items()))
                if is_dev:
                    data['devDependencies'] = sorted_deps
                else:
                    data['dependencies'] = sorted_deps

                # Write the updated JSON back to the file
                file.seek(0)
                json.dump(data, file, indent=2)
                file.truncate()
                logging.info(f"Successfully updated {package_json_path} with {package}@{version}")
            else:
                logging.info(f"{package}@{version} is already up to date in {package_json_path}")
    except Exception as e:
        logging.error(f"Error updating {package_json_path}: {str(e)}")

# [AI]: Function to determine if a Python package is a development dependency
def is_dev_dependency(package, venv_python):
    dev_keywords = ['test', 'debug', 'lint', 'format', 'doc', 'build']
    if any(keyword in package.lower() for keyword in dev_keywords):
        return True

    try:
        metadata = subprocess.run([str(venv_python), "-m", "pip", "show", package], capture_output=True, text=True).stdout
        if 'Classifier: Development Status :: 5 - Production/Stable' in metadata:
            return False
        if any(f'Classifier: Development Status :: {i}' in metadata for i in range(1, 5)):
            return True
    except subprocess.CalledProcessError:
        pass

    return False

# [AI]: Function to determine if a Node.js package is a development dependency
def is_node_dev_dependency(package):
    dev_keywords = ['test', 'dev', 'debug', 'lint', 'format', 'doc', 'build', 'eslint', 'prettier', 'jest', 'mocha', 'chai', 'webpack', 'babel', 'typescript']
    return any(keyword in package.lower() for keyword in dev_keywords)

# [AI]: Function to get the version of an installed Python package
def get_python_package_version(package_name, venv_python):
    try:
        result = subprocess.run([venv_python, '-m', 'pip', 'show', package_name], 
                                capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':')[1].strip()
    except subprocess.CalledProcessError:
        return None
    return None

# [AI]: Function to update requirements.txt with newly installed package
def update_requirements_txt(package, is_dev, venv_python):
    logging.info(f"Attempting to update requirements.txt for {package}")
    
    version = get_python_package_version(package, venv_python)
    if not version:
        logging.error(f"Could not determine version for {package}")
        return

    logging.info(f"Determined version for {package}: {version}")

    requirements_path = find_file('requirements.txt')
    if not requirements_path:
        logging.error("requirements.txt not found in the project")
        return

    logging.info(f"Found requirements.txt at: {requirements_path}")

    try:
        with open(requirements_path, 'r') as file:
            lines = file.readlines()
        logging.info(f"Successfully read {requirements_path}")

        # Remove any existing entries of the package
        original_length = len(lines)
        lines = [line for line in lines if not line.strip().startswith(f"{package}==")]
        if len(lines) < original_length:
            logging.info(f"Removed existing entries of {package}")
        else:
            logging.info(f"No entries of {package} found to remove")

        # Identify sections
        prod_start = next((i for i, line in enumerate(lines) if '# Production Dependencies' in line), -1)
        dev_start = next((i for i, line in enumerate(lines) if '# Development Dependencies' in line), -1)
        logging.info(f"Production section starts at line {prod_start}, Development section starts at line {dev_start}")

        new_line = f"{package}=={version}\n"
        
        if is_dev and dev_start != -1:
            logging.info(f"Adding {package} to Development Dependencies")
            insert_index = dev_start + 1
            while insert_index < len(lines) and lines[insert_index].strip() and not lines[insert_index].startswith('#'):
                if package < lines[insert_index].split('==')[0]:
                    break
                insert_index += 1
            lines.insert(insert_index, new_line)
        elif not is_dev and prod_start != -1:
            logging.info(f"Adding {package} to Production Dependencies")
            insert_index = prod_start + 1
            while insert_index < len(lines) and lines[insert_index].strip() and not lines[insert_index].startswith('#'):
                if package < lines[insert_index].split('==')[0]:
                    break
                insert_index += 1
            lines.insert(insert_index, new_line)
        else:
            logging.info(f"Adding new section for {package}")
            lines.append(f"\n{'# Development' if is_dev else '# Production'} Dependencies\n")
            lines.append(new_line)

        logging.info(f"Attempting to write updated content to {requirements_path}")
        with open(requirements_path, 'w') as file:
            file.writelines(lines)
        logging.info(f"Successfully wrote updated content to {requirements_path}")

        # Verify the update
        with open(requirements_path, 'r') as file:
            updated_content = file.read()
        if f"{package}=={version}" in updated_content:
            logging.info(f"Verified: {package}=={version} is now in {requirements_path}")
        else:
            logging.error(f"Verification failed: {package}=={version} not found in {requirements_path}")

        logging.debug(f"Contents of {requirements_path} after update:\n{updated_content}")
    except Exception as e:
        logging.error(f"Error updating {requirements_path}: {str(e)}")
        logging.exception("Exception details:")

def find_package_json_files(start_dir=PROJECT_ROOT):
    start_dir = Path(start_dir)
    package_json_files = []
    for root, dirs, files in os.walk(start_dir):
        if 'package.json' in files:
            package_json_files.append(Path(root) / 'package.json')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')  # don't traverse into node_modules
    return package_json_files

def update_requirements_for_installed_package(package_name, venv_python):
    version = get_python_package_version(package_name, venv_python)
    if version:
        is_dev = is_dev_dependency(package_name, venv_python)
        update_requirements_txt(package_name, is_dev, venv_python)
        logger.info(f"Updated requirements.txt for {package_name}")
    else:
        logger.warning(f"Could not find version for {package_name}. It may not be installed.")

def update_package_json_for_installed_package(package_name):
    version = get_node_package_version(package_name)
    if version:
        is_dev = is_node_dev_dependency(package_name)
        update_package_json(package_name, is_dev)
        logger.info(f"Updated package.json for {package_name}")
    else:
        logger.warning(f"Could not find version for {package_name}. It may not be installed.")

def display_venv_info(venv_path):
    print(info_message(f"Virtual environment is active at: {venv_path}"))

def main():
    if not check_python_and_npm():
        return 1

    venv_path = PROJECT_ROOT / "venv"
    create_venv(venv_path)
    venv_python = get_venv_python(venv_path)
    display_venv_info(venv_path)

    packages = get_package_input()
    
    if not packages:
        print(warning_message("\nWARNING:", "No packages entered. Nothing to install."))
        return 0

    installed_packages = []

    for prefix, package_name in packages:
        if prefix == 'npm':
            package_json_path = find_package_json()
            if not package_json_path:
                print(error_message("\nNo package.json found in the project. Cannot install npm package."))
                continue

            npm_path = get_npm_path()
            if not npm_path:
                print(error_message("\nSkipping npm package installation due to missing npm."))
                continue

            if install_node_package(package_name, package_json_path):
                update_package_json(package_json_path, package_name, is_node_dev_dependency(package_name))
                installed_packages.append(f"npm:{package_name}")
                print(success_message(f"\nSuccessfully installed {package_name}"))
        elif prefix == 'pip':
            if install_python_package(venv_path, package_name):
                is_dev = is_dev_dependency(package_name, venv_python)
                update_requirements_txt(package_name, is_dev, venv_python)
                installed_packages.append(f"pip:{package_name}")
                print(success_message(f"Updated requirements.txt for {package_name}"))
            else:
                update_requirements_for_installed_package(package_name, venv_python)

    if installed_packages:
        print(info_message("\nSummary of installed packages:"))  # Changed to info_message
        for package in installed_packages:
            print(info_message(f"- {package}"))
    else:
        print(warning_message("\nWARNING:", "No new packages were installed."))

    print()  # Add an extra line break at the end
    return 0

if __name__ == "__main__":
    sys.exit(main())