# [AI]: This file implements an automated tech stack update process.
# It provides functionality to parse Python and JavaScript dependencies and update a markdown file.
# Key features:
# - Finds required files in the project structure
# - Parses Python requirements and JavaScript package dependencies
# - Generates a formatted markdown file with the tech stack information
# - Uses colorama for colored console output

import os
from pathlib import Path
import logging
import json
import re
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

def file_path_message(message: str) -> str:
    return format_message(message, INFO_COLOR)

# [AI]: Set up logging for tracking script execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# [AI]: Determine the project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# [AI]: Function to find a file in the project directory with a maximum search depth
def find_file(filename, start_dir=PROJECT_ROOT, max_depth=5):
    start_dir = Path(start_dir)
    for root, dirs, files in os.walk(str(start_dir)):
        if filename in files:
            return Path(os.path.join(root, filename))
        if len(Path(root).relative_to(start_dir).parts) >= max_depth:
            del dirs[:]
    return None

# [AI]: Parse Python requirements file to extract production and development dependencies
def parse_requirements(requirements_path):
    with open(requirements_path, 'r') as file:
        content = file.read()
        prod_deps = re.findall(r'^(.+)==.+$', content, re.MULTILINE)
        dev_deps = re.findall(r'^(.+)==.+$', content[content.find('# Development Dependencies'):], re.MULTILINE)
    return {'production': prod_deps, 'development': dev_deps}

# [AI]: Parse package.json file to extract JavaScript dependencies and devDependencies
def parse_package_json(package_json_path):
    with open(package_json_path, 'r') as file:
        data = json.load(file)
        return {
            'dependencies': list(data.get('dependencies', {}).keys()),
            'devDependencies': list(data.get('devDependencies', {}).keys())
        }

# [AI]: Main function to update the tech stack markdown file
def update_tech_stack():
    print(info_message("\nStarting update_tech_stack.py\n"))
    print(info_message(f"Project root: {PROJECT_ROOT}"))

    # [AI]: Define files to find and store their paths
    files_to_find = ['tech_stack.md', 'requirements.txt', 'package.json']
    found_files = {}

    # [AI]: Find and log the location of each required file
    for file in files_to_find:
        found_files[file] = find_file(file)
        if found_files[file]:
            print(info_message(f"Found {file} at: {file_path_message(str(found_files[file]))}"))
        else:
            print(warning_message("Warning:", f"Could not find {file}"))

    # [AI]: Check if all required files are found, abort if not
    if not all(found_files.values()):
        print(error_message("One or more required files not found. Aborting."))
        return

    print(info_message("\nParsing files..."))
    # [AI]: Parse Python and JavaScript package information
    python_packages = parse_requirements(found_files['requirements.txt'])
    js_packages = parse_package_json(found_files['package.json'])
    print(f"{SUCCESS_COLOR}Parsed:{Style.RESET_ALL} Successfully parsed requirements.txt and package.json")

    # [AI]: Generate content for the tech stack markdown file
    content = "# Tech Stack\n\n"
    content += "## Python Packages\n\n"
    content += "### Production Dependencies\n" + "\n".join(f"- {pkg}" for pkg in python_packages['production']) + "\n\n"
    content += "### Development Dependencies\n" + "\n".join(f"- {pkg}" for pkg in python_packages['development']) + "\n\n"
    content += "## JavaScript Packages\n\n"
    content += "### Dependencies\n" + "\n".join(f"- {pkg}" for pkg in js_packages['dependencies']) + "\n\n"
    content += "### DevDependencies\n" + "\n".join(f"- {pkg}" for pkg in js_packages['devDependencies']) + "\n\n"

    print(info_message("Updating tech_stack.md..."))
    # [AI]: Write the generated content to the tech_stack.md file
    try:
        with open(found_files['tech_stack.md'], 'w') as file:
            file.write(content)
        relative_path = found_files['tech_stack.md'].relative_to(PROJECT_ROOT)
        print(f"{SUCCESS_COLOR}Updated:{Style.RESET_ALL} Tech stack in {file_path_message(str(relative_path))}")
    except IOError as e:
        print(error_message(f"Error writing to file: {e}"))

    print(success_message("\nTech stack update completed successfully."))
    print()  # Add a final line break

# [AI]: Execute the update_tech_stack function if the script is run directly
if __name__ == "__main__":
    update_tech_stack()