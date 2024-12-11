# [AI]: This file implements a local environment preparation script for a project.
# It provides functionality to check and set up the necessary environment for development.
# Key features:
# - Virtual environment verification
# - Dependency checking
# - Pip upgrade
# - Colorama installation
# - Logging for debugging

import os
import sys
import subprocess
import logging

# [AI]: Configure logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# [AI]: Helper function to run shell commands and handle errors
def run_command(command):
    """Run a shell command and return its output."""
    try:
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return e.output

# [AI]: Utility functions for formatting console output
def print_section(title):
    """Print a formatted section title."""
    print(f"\n{'=' * 50}")
    print(f"{title}")
    print(f"{'=' * 50}")

def print_step(step):
    """Print a formatted step title."""
    print(f"\n{step}")
    print(f"{'-' * 50}")

# [AI]: Check if the virtual environment exists and is activated
def check_venv():
    """Check if venv exists and is active."""
    venv_path = os.path.join(os.getcwd(), 'venv')
    if not os.path.exists(venv_path):
        print("Virtual environment not found.")
        print("To create a venv, run:")
        print("    python -m venv venv")
        print("To activate the venv, run:")
        print("    .\\venv\\Scripts\\Activate.ps1")
        print()  # Add a line break here
        return False
    
    if sys.prefix == sys.base_prefix:
        print("Virtual environment is not activated.")
        print("To activate the venv, run:")
        print("    .\\venv\\Scripts\\Activate.ps1")
        print()  # Add a line break here
        return False
    
    return True

# [AI]: Verify the presence of required development dependencies
def check_dependencies():
    """Check for the presence of required dependencies."""
    dependencies = {
        'python': 'python --version',
        'node': 'node --version',
        'npm': 'npm --version',
        'postgres': 'psql --version'
    }

    all_dependencies_installed = True
    for dep, command in dependencies.items():
        output = run_command(command)
        if output:
            print(f"✓ {dep.capitalize()} is installed: {output.strip()}")
        else:
            print(f"✗ {dep.capitalize()} is not installed or not in PATH.")
            all_dependencies_installed = False
    
    return all_dependencies_installed

# [AI]: Upgrade pip to ensure the latest version is used
def upgrade_pip():
    """Upgrade pip to the latest version."""
    print("Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("Pip upgraded successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to upgrade pip.")
        return False

# [AI]: Install colorama for enhanced console output
def install_colorama():
    """Install colorama in the virtual environment."""
    print("Installing colorama...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
        print("Colorama installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install colorama.")
        return False

# [AI]: Main function to orchestrate the environment preparation steps
def main():
    try:
        print_section("Starting local preparation for this project")
        
        # [AI]: Step 1: Verify virtual environment
        logging.debug("Starting Step 1: Checking environment")
        print_step("Step 1: Checking environment")
        venv_status = check_venv()
        if not venv_status:
            print("Please create and/or activate the virtual environment before proceeding.")
            print()  # Add another line break here
            return
        print("Virtual environment is active and ready.")

        # [AI]: Step 2: Check for required dependencies
        logging.debug("Starting Step 2: Checking dependencies")
        print_step("Step 2: Checking dependencies")
        dependencies_setup = check_dependencies()
        if not dependencies_setup:
            print("Please install missing dependencies before proceeding.")
            return
        print("All required dependencies are installed.")

        # [AI]: Step 3: Upgrade pip to latest version
        logging.debug("Starting Step 3: Upgrading pip")
        print_step("Step 3: Upgrading pip")
        pip_upgrade = upgrade_pip()
        if not pip_upgrade:
            print("Failed to upgrade pip. Please upgrade manually before proceeding.")
            return
        print("Pip has been upgraded to the latest version.")

        # [AI]: Step 4: Install colorama for enhanced console output
        logging.debug("Starting Step 4: Installing colorama")
        print_step("Step 4: Installing colorama")
        if not install_colorama():
            print("Failed to install colorama. Please install manually before proceeding.")
            return
        print("Colorama has been installed successfully.")

        print_section("Local preparation completed successfully")
        print("You can now proceed with the provisioning script.\n")

    except Exception as e:
        # [AI]: Log unexpected errors for debugging
        logging.exception("An unexpected error occurred:")
        print("An unexpected error occurred. Please check the logs for details.\n")
    except KeyboardInterrupt:
        # [AI]: Handle user interruption gracefully
        print("\nSetup interrupted by user. Exiting...\n")
        sys.exit(1)

# [AI]: Entry point of the script
if __name__ == "__main__":
    main()


