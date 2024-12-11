# [AI]: This file implements a local environment provisioning script for a project.
# It provides functionality to set up and configure various components of the development environment.
# Key features:
# - Installing project dependencies
# - Updating tech stack
# - Setting up project name
# - Database setup and connection
# - Running update scripts
# - Starting backend and frontend
# - Running backup scripts
# - Testing CRUD operations

import os
import sys
import subprocess
import itertools
import logging
import time
import queue
import threading
from colorama import init, Fore, Style

# [AI]: Initialize colorama for cross-platform colored output
init(autoreset=True)

# [AI]: Configure logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# [AI]: Execute a shell command and return its output, handling potential errors
def run_command(command):
    """Run a shell command and return its output."""
    try:
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return e.output

# [AI]: Print a formatted section title for better visual separation in the console
def print_section(title):
    """Print a formatted section title."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 50}")
    print(f"{title}")
    print(f"{'=' * 50}{Style.RESET_ALL}")

# [AI]: Print a formatted step title for better visual separation of individual steps
def print_step(step):
    """Print a formatted step title."""
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{step}")
    print(f"{'-' * 50}{Style.RESET_ALL}")

# [AI]: Execute a Python script with a timeout, providing visual feedback on progress
def run_script(script_path, timeout=900):
    print(f"\n{Fore.YELLOW}Executing: {os.path.basename(script_path)}")
    print("-" * 50)
    try:
        process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        last_line = ""
        start_time = time.time()
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            # [AI]: Handle different types of output for better user feedback
            if "Installing collected packages" in line:
                sys.stdout.write(f"\r{line}")
                sys.stdout.flush()
            elif "Installing Node.js packages" in line:
                sys.stdout.write(f"\r{line} {next(spinner)}")
                sys.stdout.flush()
                last_line = line
            elif line:
                if last_line.startswith("Installing Node.js packages"):
                    sys.stdout.write("\n")
                print(line)
                last_line = line
            # [AI]: Check for timeout and terminate the process if exceeded
            if time.time() - start_time > timeout:
                process.kill()
                raise subprocess.TimeoutExpired(script_path, timeout)
        process.stdout.close()
        return_code = process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, script_path)
        print(f"\n{Fore.GREEN}Completed: {os.path.basename(script_path)}")
        return True
    except subprocess.TimeoutExpired as e:
        print(f"{Fore.RED}Error: {os.path.basename(script_path)} timed out after {timeout} seconds.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error running {os.path.basename(script_path)}:")
        print(e.output.strip())
        return False

# [AI]: Prompt the user for input and return a boolean based on their response
def prompt_user(message):
    """Prompt the user with a message and return True if they respond with 'y'."""
    try:
        response = input(f"{Fore.YELLOW}{message}{Style.RESET_ALL}").strip().lower() == 'y'
        logging.debug(f"User response: {response}")
        return response
    except EOFError:
        logging.debug("EOFError encountered while prompting user.")
        return False

# [AI]: Execute a Python script with real-time logging of its output
def run_script_with_logging(script_path):
    print(f"\n{Fore.YELLOW}Executing: {os.path.basename(script_path)}")
    print("-" * 50)
    try:
        process = subprocess.Popen([sys.executable, script_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT, 
                                   universal_newlines=True, 
                                   bufsize=1)
        
        output_queue = queue.Queue()
        
        # [AI]: Read process output in a separate thread to avoid blocking
        def read_output(proc, queue):
            for line in iter(proc.stdout.readline, ''):
                queue.put(line.strip())
            proc.stdout.close()
        
        output_thread = threading.Thread(target=read_output, args=(process, output_queue))
        output_thread.daemon = True
        output_thread.start()
        
        # [AI]: Print output in real-time while the process is running
        while process.poll() is None:
            try:
                line = output_queue.get(timeout=0.1)
                print(line)
            except queue.Empty:
                continue
        
        # [AI]: Print any remaining output after the process has finished
        while not output_queue.empty():
            print(output_queue.get())
        
        output_thread.join(timeout=5)  # Wait for up to 5 seconds
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, script_path)
        
        print(f"\n{Fore.GREEN}Completed: {os.path.basename(script_path)}")
        return True, ""
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error running {os.path.basename(script_path)}:")
        print(e.output.strip() if e.output else "No error output available")
        return False, e.output if e.output else ""
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

# [AI]: Set up the database by running a separate script and handling user input
def setup_database():
    print("You will be prompted to enter database details.")
    print("Please have your PostgreSQL admin password ready.\n")

    print(f"\n{Fore.YELLOW}Executing: create_new_database.py")
    print("-" * 50)

    script_path = os.path.join('scripts', 'database', 'create_new_database.py')

    try:
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running create_new_database.py: {e}")
        return False
    except KeyboardInterrupt:
        print("\nSetup interrupted by user. Exiting...")
        return False

    return True

# [AI]: Attempt to connect to the database with a timeout
def connect_database():
    connect_script_path = os.path.join('scripts', 'database', 'connect_database.py')
    success, output = run_script_with_logging(connect_script_path)
    
    # [AI]: Add a timeout for database connection attempts
    timeout = 30  # 30 seconds
    start_time = time.time()
    while time.time() - start_time < timeout:
        if success:
            print(f"{Fore.GREEN}Successfully connected to the database.")
            return True
        time.sleep(1)
    
    print(f"{Fore.RED}Failed to connect to the database or operation timed out. Please check the error messages above.")
    return False

# [AI]: Verify that the tech stack file contains both Python and JavaScript dependencies
def check_tech_stack():
    """Check the contents of tech_stack.md to ensure both Python and JavaScript dependencies are listed."""
    tech_stack_path = os.path.join(os.getcwd(), 'workspace', 'files', 'tech_stack.md')
    if not os.path.exists(tech_stack_path):
        print(f"{Fore.RED}tech_stack.md not found. Please ensure the file exists and try again.")
        return False

    with open(tech_stack_path, 'r') as file:
        contents = file.read()
        if 'Python' in contents and 'JavaScript' in contents:
            print(f"{Fore.GREEN}Tech stack has been updated successfully.")
            return True
        else:
            print(f"{Fore.RED}Tech stack is missing Python or JavaScript dependencies. Please update manually.")
            return False

# [AI]: Execute backup scripts to create a backup folder and perform a manual backup
def run_backup_scripts():
    backup_folder_script = os.path.join('scripts', 'backups', 'backup_create_folder.py')
    backup_manual_script = os.path.join('scripts', 'backups', 'backup_manual.py')

    try:
        # [AI]: Run backup folder creation script
        print("\nBackup folder will now be created.")
        print(f"{Fore.YELLOW}Executing: {os.path.basename(backup_folder_script)}")
        print("-" * 50)
        subprocess.run([sys.executable, backup_folder_script], check=True)
        
        # [AI]: Run manual backup script
        print("\nManual backup will now be created.")
        print(f"{Fore.YELLOW}Executing: {os.path.basename(backup_manual_script)}")
        print("-" * 50)
        subprocess.run([sys.executable, backup_manual_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error occurred while running backup scripts: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Setup interrupted by user. Exiting...")
        return False

    return True

def run_alembic_migration():
    logging.debug("Starting Alembic initial migration")
    print_step("Running Alembic initial migration")
    alembic_script_path = os.path.join('scripts', 'database', 'alembic_initial_migration.py')
    
    print(f"{Fore.YELLOW}Warning: This will reset the database for a fresh start.")
    user_input = input("Do you want to proceed with the initial migration? (yes/no): ").lower()
    
    if user_input != 'yes':
        print("Alembic migration aborted.")
        return False

    try:
        result = subprocess.run([sys.executable, alembic_script_path, '--yes'], 
                                capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"{Fore.GREEN}Alembic initial migration completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Failed to run Alembic initial migration. Error:")
        print(e.output)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"{Fore.RED}Unexpected error running Alembic initial migration:")
        print(traceback.format_exc())
        return False

# [AI]: Main function to orchestrate the entire local setup process
def main():
    try:
        print_section("Starting local setup for this project")
        
        # [AI]: Step 1: Install project dependencies
        logging.debug("Starting Step 1: Installing project dependencies")
        print_step("Step 1: Installing project dependencies")
        install_script_path = os.path.join('scripts', 'installs', 'install_initial_dependencies.py')
        print(f"{Fore.YELLOW}This step will install Python and npm dependencies.")
        print(f"{Fore.YELLOW}You'll see a progress bar for Python packages and a spinner for npm packages.")
        print(f"{Fore.YELLOW}This process may take up to 15 minutes. Please be patient.")
        if not run_script(install_script_path):
            print(f"{Fore.RED}Failed to install project dependencies. Please check the error messages above.")
            return
        print(f"{Fore.GREEN}Project dependencies have been successfully installed.")

        # [AI]: Step 2: Update tech stack
        logging.debug("Starting Step 2: Updating tech stack")
        print_step("Step 2: Updating tech stack")
        tech_stack_script_path = os.path.join('scripts', 'updates', 'update_tech_stack.py')
        if not run_script(tech_stack_script_path):
            print(f"{Fore.RED}Failed to update tech stack. Please check the error messages above.")
            return

        if not check_tech_stack():
            print(f"{Fore.RED}Tech stack update failed. Please update manually.")
            return

        # [AI]: Step 3: Set up project name
        logging.debug("Starting Step 3: Setting up project name")
        print_step("Step 3: Setting up project name")
        project_name_script = os.path.join('scripts', 'devops', 'lcl_project_name.py')
        if not run_script(project_name_script):
            print(f"{Fore.RED}Failed to set up project name. Please check the error messages above.")
            return
        print(f"{Fore.GREEN}Project name has been set up successfully.")

        # [AI]: Step 4: Set up and connect to the database
        logging.debug("Starting Step 4: Setting up database")
        print_step("Step 4: Setting up database")
        if setup_database():
            print("Database setup completed successfully.")
            if connect_database():
                print("Database connection established successfully.")
                
                # [AI]: New Step: Run Alembic initial migration
                if not run_alembic_migration():
                    print("Failed to complete Alembic migration. Stopping setup process.")
                    return
            else:
                print("Failed to connect to the database. Please check the errors and try again.")
                return
        else:
            print("Database setup failed. Please check the errors and try again.")
            return

        # [AI]: Step 5: Run update scripts
        logging.debug("Starting Step 5: Running update scripts")
        print_step("Step 5: Running update scripts")
        update_script = os.path.join('scripts', 'updates', 'update_all.py')
        if not run_script(update_script):
            print(f"{Fore.RED}Failed to run update scripts. Please check the error messages above.")
            return
        print(f"{Fore.GREEN}All update scripts have been executed successfully.")

        # [AI]: Step 6: Start backend and frontend
        logging.debug("Starting Step 6: Starting backend and frontend")
        print_step("Step 6: Starting backend and frontend")
        print(f"{Fore.YELLOW}\nPlease open two separate terminals and run the following commands:")
        print(f"{Fore.YELLOW}Terminal 1: python scripts/start/start_backend.py")
        print(f"{Fore.YELLOW}Terminal 2: python scripts/start/start_frontend.py")
        
        # [AI]: Ensure the prompt is displayed and add a timeout
        logging.debug("Prompting user to confirm backend and frontend are running")
        if not prompt_user("\nAre the backend and frontend running fine? (y/n): "):
            print(f"{Fore.RED}Setup interrupted. Please continue the rest of the process manually.\n")
            return

        # [AI]: Step 7: Run backup scripts
        logging.debug("Starting Step 7: Running backup scripts")
        print_step("Step 7: Running backup scripts")
        if not run_backup_scripts():
            print(f"{Fore.RED}Failed to run backup scripts. Please check the error messages above.")
            return
        print(f"{Fore.GREEN}Backup scripts completed successfully.")

        # [AI]: Step 8: Test CRUD operations
        logging.debug("Starting Step 8: Testing CRUD operations")
        print_step("Step 8: Testing CRUD operations")
        print(f"{Fore.YELLOW}\nPlease test CRUD operations from the frontend app.")
        if not prompt_user("Did the CRUD operations work correctly? (y/n): "):
            print(f"{Fore.RED}CRUD operations test failed. Exiting this script. Please continue from this step manually.\n")
            return

        print_section("Local setup completed successfully")
        print(f"{Fore.GREEN}You can now start using your development environment\n")

    except Exception as e:
        logging.exception("An unexpected error occurred:")
        print(f"{Fore.RED}An unexpected error occurred. Please check the logs for details.\n")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Setup interrupted by user. Exiting...\n")
        sys.exit(1)

if __name__ == "__main__":
    main()